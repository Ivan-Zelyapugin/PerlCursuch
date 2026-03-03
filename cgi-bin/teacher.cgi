#!/usr/bin/perl
use strict;
use warnings;
use utf8;

use FindBin qw($Bin);
use lib $Bin;

use CGI qw(:standard);
use Encode qw(decode);

require "db.pm";

my $data = "$Bin/./data";   

my %weekday_name = (
  1 => "Понедельник",
  2 => "Вторник",
  3 => "Среда",
  4 => "Четверг",
  5 => "Пятница",
  6 => "Суббота",
);

sub esc {
  my ($s) = @_;
  $s //= "";
  $s =~ s/&/&amp;/g;
  $s =~ s/</&lt;/g;
  $s =~ s/>/&gt;/g;
  $s =~ s/"/&quot;/g;
  return $s;
}

sub dec_param {
  my ($cgi, $name) = @_;
  my $v = $cgi->param($name);
  $v = "" if !defined $v;

  $v = decode("UTF-8", $v, 1);   
  $v =~ s/^\s+|\s+$//g;
  return $v;
}

sub urlenc {
  my ($s) = @_;
  return CGI::escape($s // "");
}

sub html_header {
  my ($title) = @_;
  print "Content-Type: text/html; charset=utf-8\n\n";
  print <<"HTML";
<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>$title</title>
  <link rel="stylesheet" href="/www/style.css">

  <script>
    function showHelp() {
      alert("Подсказка:\\n1) Введите фамилию (или её часть).\\n2) Выберите преподавателя из списка.\\n\\nКнопка «Скопировать» копирует таблицу занятий.");
    }

    async function copyTeacherLoad() {
      const table = document.getElementById("load-table");
      if (!table) { alert("Таблица занятий не найдена."); return; }

      let out = "";
      const rows = table.querySelectorAll("tr");
      rows.forEach((tr, idx) => {
        const cells = tr.querySelectorAll(idx === 0 ? "th" : "td");
        const line = Array.from(cells).map(c => c.textContent.trim()).join(" | ");
        out += line + "\\n";
      });

      out = out.trim();
      if (!out) { alert("Нечего копировать."); return; }

      try {
        await navigator.clipboard.writeText(out);
        alert("Скопировано в буфер обмена.");
      } catch (e) {
        const ta = document.createElement("textarea");
        ta.value = out;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        document.body.removeChild(ta);
        alert("Скопировано (fallback).");
      }
    }

    function printPage() { window.print(); }
  </script>
</head>
<body>
<header>
  <nav>
    <a href="/www/index.html">Главная</a>
    <a href="/www/history.html">История</a>
    <a href="/www/departments.html">Кафедры</a>
    <a href="/www/schedule.html">Расписание</a>
    <a href="/www/reception.html">Часы приёма</a>
    <a href="/www/teacher.html">Преподаватели</a>
  </nav>
</header>

<div class="fab-nav" aria-label="Быстрая навигация">
  <a class="fab" href="#top" title="В начало">↑</a>
  <a class="fab" href="#bottom" title="В конец">↓</a>
</div>

<div class="container">
  <a id="top"></a>
HTML
}

sub html_footer {
  print <<"HTML";
  <a id="bottom"></a>
</div>

<div class="footer">
  © Факультет вычислительной техники
</div>
</body>
</html>
HTML
}

sub get_group_name {
  my ($gid) = @_;
  my $rows = Db::find_by("$data/groups.db", "group_id", $gid);
  return $gid if !@$rows;
  return $rows->[0]->{name} || $gid;
}

sub get_all_schedule_rows {
  return Db::get_all("$data/schedule.db");
}

sub find_teachers_by_query {
  my ($q) = @_;
  my $all = get_all_schedule_rows();

  my %uniq;
  my $q_lc = lc($q);

  for my $r (@$all) {
    my $t = $r->{teacher} // "";
    next if $t eq "";
    if (index(lc($t), $q_lc) != -1) {
      $uniq{$t} = 1;
    }
  }

  my @list = sort keys %uniq;
  return \@list;
}

sub get_teacher_load {
  my ($teacher_exact) = @_;
  my $all = get_all_schedule_rows();

  my @rows = grep {
    defined($_->{teacher}) && $_->{teacher} eq $teacher_exact
  } @$all;

  @rows = sort {
    ($a->{weekday} <=> $b->{weekday}) ||
    ($a->{pair_no} <=> $b->{pair_no}) ||
    (($a->{group_id}||0) <=> ($b->{group_id}||0))
  } @rows;

  return \@rows;
}

my $cgi = CGI->new;

my $q       = dec_param($cgi, "q");
my $teacher = dec_param($cgi, "teacher");

my $title = "Поиск преподавателя";
$title = "Занятия — " . esc($teacher) if $teacher ne "";

html_header($title);

my $hero_text = ($teacher ne "")
  ? ("Выбран преподаватель: <b>" . esc($teacher) . "</b>.")
  : "";

print qq{
  <section class="hero" aria-label="Первый экран">
    <div class="hero-inner">
      <div>
        <h1>Поиск преподавателя</h1>
        <p>$hero_text</p>

        <div class="hero-actions" style="display:flex;flex-wrap:wrap;gap:10px">
          <a class="btn primary" href="/www/teacher.html">Новый поиск</a>
          <a class="btn" href="#content">К результату</a>
          <a class="btn" href="/www/index.html">На главную</a>

          <button type="button" class="btn" onclick="location.href='/www/teacher.html'"
                  style="display:inline-flex;align-items:center;gap:8px">
            К поиску
          </button>

          <button type="button" class="btn" onclick="showHelp()">Справка</button>
          <button type="button" class="btn" onclick="copyTeacherLoad()">Скопировать</button>
          <button type="button" class="btn" onclick="printPage()">Печать</button>
        </div>
      </div>

      <div class="hero-media">
        <img src="/www/img/auditor.png" alt="Аудитория факультета">
      </div>
    </div>
  </section>
};

print qq{
  <section class="card" id="content" style="margin-top:16px">
    <div class="card-header"><h2>Результат</h2></div>
    <div class="card-body">
};

if ($teacher eq "") {
  if ($q eq "") {
    print qq{
      <p>Запрос не задан. Перейдите на страницу поиска и введите фамилию.</p>
      <p style="margin-top:12px">
        <a class="btn primary" href="/www/teacher.html">Перейти к поиску</a>
        <a class="btn" href="#top">Наверх</a>
      </p>
    };
    print qq{</div></section>};
    html_footer();
    exit;
  }

  my $teachers = find_teachers_by_query($q);

  if (!@$teachers) {
    print qq{
      <p>По запросу <b>} . esc($q) . qq{</b> ничего не найдено.</p>
      <p class="muted">Попробуйте другую часть фамилии или проверьте написание.</p>
      <p style="margin-top:12px">
        <a class="btn primary" href="/www/teacher.html">Новый поиск</a>
        <a class="btn" href="#top">Наверх</a>
      </p>
    };
    print qq{</div></section>};
    html_footer();
    exit;
  }

  print qq{
    <p>Найдены преподаватели по запросу <b>} . esc($q) . qq{</b>:</p>
    <table>
      <tr>
        <th>Преподаватель</th>
        <th>Действие</th>
      </tr>
  };

  for my $t (@$teachers) {
    my $link = "/cgi-bin/teacher.cgi?q=" . urlenc($q) . "&teacher=" . urlenc($t);
    print qq{
      <tr>
        <td>} . esc($t) . qq{</td>
        <td><a href="$link">Открыть занятия</a></td>
      </tr>
    };
  }

  print qq{
    </table>
    <p style="margin-top:12px">
      <a class="btn" href="/www/teacher.html">Новый поиск</a>
      <a class="btn" href="#top">Наверх</a>
    </p>
    </div>
  </section>
  };

  html_footer();
  exit;
}

my $load = get_teacher_load($teacher);

if (!@$load) {
  print qq{
    <p>Для преподавателя <b>} . esc($teacher) . qq{</b> в расписании нет записей.</p>
    <p class="muted">Если вы выбирали из списка, проверьте заполнение поля teacher в schedule.db.</p>
    <p style="margin-top:12px">
      <a class="btn primary" href="/www/teacher.html">Новый поиск</a>
      <a class="btn" href="#top">Наверх</a>
    </p>
  };
  print qq{</div></section>};
  html_footer();
  exit;
}

print qq{
  <p>Ниже показаны занятия преподавателя <b>} . esc($teacher) . qq{</b> по текущему расписанию.</p>
  <p style="margin-top:12px">
    <a class="btn" href="/www/teacher.html">Новый поиск</a>
    <a class="btn" href="#top">Наверх</a>
    <a class="btn" href="#bottom">В конец</a>
  </p>
</div></section>
};

print qq{
  <section class="card" style="margin-top:16px">
    <div class="card-header"><h2>Занятия</h2></div>
    <div class="card-body">
      <table id="load-table">
        <tr>
          <th>День</th>
          <th>Пара</th>
          <th>Время</th>
          <th>Группа</th>
          <th>Дисциплина</th>
          <th>Аудитория</th>
        </tr>
};

for my $r (@$load) {
  my $wd  = int($r->{weekday} || 0);
  my $day = $weekday_name{$wd} || "—";
  my $gid = $r->{group_id} // "";
  my $gname = get_group_name($gid);

  print qq{
        <tr>
          <td>} . esc($day) . qq{</td>
          <td>} . esc($r->{pair_no}) . qq{</td>
          <td>} . esc($r->{time}) . qq{</td>
          <td>} . esc($gname) . qq{</td>
          <td>} . esc($r->{subject}) . qq{</td>
          <td>} . esc($r->{room}) . qq{</td>
        </tr>
  };
}

print qq{
      </table>
      <p style="margin-top:12px">
        <a class="btn" href="#top">Наверх</a>
        <a class="btn" href="/www/teacher.html">Новый поиск</a>
      </p>
    </div>
  </section>
};

html_footer();
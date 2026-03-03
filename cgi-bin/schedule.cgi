#!/usr/bin/perl
use strict;
use warnings;
use utf8;

use FindBin qw($Bin);
use lib $Bin;

use CGI qw(:standard);

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
      alert("Подсказка:\\n1) Группу выбирают на странице «Расписание».\\n2) Здесь показаны занятия выбранной группы.\\n\\nКнопки: «Скопировать» копирует расписание в буфер, «Печать» открывает окно печати.");
    }

    async function copySchedule() {
      const root = document.getElementById("schedule-root");
      if (!root) {
        alert("Не найден блок расписания.");
        return;
      }

      let out = "";
      const dayCards = root.querySelectorAll("[data-day]");
      dayCards.forEach(card => {
        const day = card.getAttribute("data-day") || "";
        out += day + "\\n";

        const rows = card.querySelectorAll("table tr");
        rows.forEach((tr, idx) => {
          if (idx === 0) return; 
          const cells = tr.querySelectorAll("td");
          const line = Array.from(cells).map(td => td.textContent.trim()).join(" | ");
          if (line) out += "  " + line + "\\n";
        });

        out += "\\n";
      });

      out = out.trim();
      if (!out) {
        alert("Нечего копировать: таблицы пустые.");
        return;
      }

      try {
        await navigator.clipboard.writeText(out);
        alert("Расписание скопировано в буфер обмена.");
      } catch (e) {
        const ta = document.createElement("textarea");
        ta.value = out;
        document.body.appendChild(ta);
        ta.select();
        document.execCommand("copy");
        document.body.removeChild(ta);
        alert("Расписание скопировано (fallback).");
      }
    }

    function printSchedule() {
      window.print();
    }
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
  return undef if !@$rows;
  return $rows->[0]->{name};
}

sub get_group_schedule_rows {
  my ($gid) = @_;
  my $rows = Db::find_by("$data/schedule.db", "group_id", $gid);

  my @sorted = sort {
    ($a->{weekday} <=> $b->{weekday}) ||
    ($a->{pair_no} <=> $b->{pair_no})
  } @$rows;

  return \@sorted;
}

sub group_by_weekday {
  my ($rows) = @_;
  my %by;
  for my $r (@$rows) {
    my $wd = int($r->{weekday} || 0);
    push @{$by{$wd}}, $r if $wd >= 1 && $wd <= 6;
  }
  return \%by;
}

my $q = CGI->new;
my $group_id = $q->param("group_id") // "";
$group_id =~ s/\s+//g;

my $group_name = $group_id ? get_group_name($group_id) : undef;
my $title = $group_name ? "Расписание — " . esc($group_name) : "Расписание";

html_header($title);

my $hero_text = $group_name
  ? "Выбрана группа: <b>" . esc($group_name) . "</b>."
  : "Выберите группу на странице расписания, чтобы увидеть занятия.";

print qq{
  <section class="hero" aria-label="Первый экран">
    <div class="hero-inner">
      <div>
        <h1>Расписание занятий</h1>
        <p>$hero_text</p>

        <div class="hero-actions">
          <a class="btn primary" href="/www/schedule.html">Сменить группу</a>
          <a class="btn" href="#content">К расписанию</a>
          <a class="btn" href="/www/index.html">На главную</a>

          <!-- Кнопка-картинка (image button) -->
          <button 
            type="button" 
            class="btn" 
            onclick="location.href='/www/schedule.html'"
            style="display:inline-flex;align-items:center;gap:8px"
          >
            К выбору группы
          </button>

          <!-- JS-кнопка со сценарием -->
          <button type="button" class="btn" onclick="showHelp()">Справка</button>
          <button type="button" class="btn" onclick="copySchedule()">Скопировать</button>
          <button type="button" class="btn" onclick="printSchedule()">Печать</button>
        </div>
      </div>

      <div class="hero-media">
        <img src="/www/img/auditor.png" alt="Аудитория факультета">
      </div>
    </div>
  </section>
};

print qq{
  <section class="card" id="list" style="margin-top:16px">
    <div class="card-header"><h2>Разделы страницы</h2></div>
    <div class="card-body">
      <ul class="list">
        <li><a href="#content">Результат</a></li>
        <li><a href="#day1">Понедельник</a></li>
        <li><a href="#day2">Вторник</a></li>
        <li><a href="#day3">Среда</a></li>
        <li><a href="#day4">Четверг</a></li>
        <li><a href="#day5">Пятница</a></li>
        <li><a href="#day6">Суббота</a></li>
      </ul>
      <p class="muted">
        Быстрые переходы: <a href="#top">в начало</a> · <a href="#bottom">в конец</a>
      </p>
    </div>
  </section>
};

print qq{
  <section class="card" id="content" style="margin-top:16px">
    <div class="card-header"><h2>Результат</h2></div>
    <div class="card-body">
};

if (!$group_id) {
  print qq{
    <p>Группа не выбрана. Вернитесь на страницу расписания и выберите группу.</p>
    <p style="margin-top:12px">
      <a class="btn primary" href="/www/schedule.html">Выбрать группу</a>
      <a class="btn" href="/www/index.html">На главную</a>
      <a class="btn" href="#top">Наверх</a>
    </p>
  };
  print qq{</div></section>};
  html_footer();
  exit;
}

if (!$group_name) {
  print qq{
    <p>Неизвестная группа: <b>} . esc($group_id) . qq{</b>.</p>
    <p class="muted">Проверьте выбор в списке групп и повторите попытку.</p>
    <p style="margin-top:12px">
      <a class="btn primary" href="/www/schedule.html">Выбрать группу</a>
      <a class="btn" href="#top">Наверх</a>
    </p>
  };
  print qq{</div></section>};
  html_footer();
  exit;
}

my $rows = get_group_schedule_rows($group_id);

if (!@$rows) {
  print qq{
    <p>Расписание для группы <b>} . esc($group_name) . qq{</b> пока не заполнено.</p>
    <p class="muted">Добавьте записи в schedule.db через init-скрипт.</p>
    <p style="margin-top:12px">
      <a class="btn" href="/www/schedule.html">Сменить группу</a>
      <a class="btn" href="#top">Наверх</a>
    </p>
  };
  print qq{</div></section>};
  html_footer();
  exit;
}

print qq{
  <p>Ниже приведено расписание для группы <b>} . esc($group_name) . qq{</b>.</p>
  <p style="margin-top:12px">
    <a class="btn" href="/www/schedule.html">Сменить группу</a>
    <a class="btn" href="#top">Наверх</a>
    <a class="btn" href="#bottom">В конец</a>
  </p>
</div></section>
};

my $by = group_by_weekday($rows);

print qq{<div id="schedule-root">};

for my $wd (1..6) {
  my $day_rows = $by->{$wd} || [];
  my $day_title = $weekday_name{$wd};

  print qq{
    <article class="card" id="day$wd" data-day="$day_title" style="margin-top:16px">
      <div class="card-header"><h2>} . esc($day_title) . qq{</h2></div>
      <div class="card-body">
  };

  if (!@$day_rows) {
    print qq{<p class="muted">Занятий нет.</p>};
  } else {
    print qq{
      <table>
        <tr>
          <th>Пара</th>
          <th>Время</th>
          <th>Дисциплина</th>
          <th>Преподаватель</th>
          <th>Аудитория</th>
        </tr>
    };

    for my $r (@$day_rows) {
      print qq{
        <tr>
          <td>} . esc($r->{pair_no}) . qq{</td>
          <td>} . esc($r->{time}) . qq{</td>
          <td>} . esc($r->{subject}) . qq{</td>
          <td>} . esc($r->{teacher}) . qq{</td>
          <td>} . esc($r->{room}) . qq{</td>
        </tr>
      };
    }

    print qq{</table>};
  }

  print qq{
        <p style="margin-top:12px">
          <a class="btn" href="#top">Наверх</a>
          <a class="btn" href="#content">К результату</a>
        </p>
      </div>
    </article>
  };
}

print qq{</div>}; 

html_footer();

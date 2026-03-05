#!/usr/bin/perl
use strict;
use warnings;
use utf8;

use FindBin qw($Bin);
use lib $Bin;

use CGI qw(:standard);
use Encode qw(decode);
use DBI;

my $db_path = "$Bin/data/site.sqlite";

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

sub db_connect {
  my $dbh = DBI->connect(
    "dbi:SQLite:dbname=$db_path",
    "",
    "",
    {
      RaiseError     => 1,
      PrintError     => 0,
      AutoCommit     => 1,
      sqlite_unicode => 1,
    }
  );
  $dbh->do("PRAGMA foreign_keys = ON");
  return $dbh;
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

sub find_teachers_by_query {
  my ($dbh, $q) = @_;
  my $sth = $dbh->prepare(q{
    SELECT teacher_id, name
    FROM teachers
    WHERE name LIKE '%' || ? || '%'
    ORDER BY name ASC
    LIMIT 200
  });
  $sth->execute($q);

  my @list;
  while (my $r = $sth->fetchrow_hashref) {
    push @list, $r;
  }
  return \@list;
}

sub resolve_teacher {
  my ($dbh, $teacher_param) = @_;

  return undef if !defined($teacher_param) || $teacher_param eq "";

  # Если пришёл teacher_id
  if ($teacher_param =~ /^\d+$/) {
    my $sth = $dbh->prepare(q{
      SELECT teacher_id, name
      FROM teachers
      WHERE teacher_id = ?
    });
    $sth->execute($teacher_param);
    return $sth->fetchrow_hashref;
  }

  # Если пришло имя (на случай старых ссылок)
  my $sth = $dbh->prepare(q{
    SELECT teacher_id, name
    FROM teachers
    WHERE name = ?
  });
  $sth->execute($teacher_param);
  return $sth->fetchrow_hashref;
}

sub get_teacher_load {
  my ($dbh, $teacher_id) = @_;

  my $sth = $dbh->prepare(q{
    SELECT
      e.weekday,
      e.pair_no,
      ts.time AS time,
      g.name  AS group_name,
      s.name  AS subject,
      r.name  AS room,
      e.note  AS note
    FROM schedule_entries e
    JOIN time_slots ts ON ts.pair_no = e.pair_no
    JOIN groups     g  ON g.group_id = e.group_id
    JOIN subjects   s  ON s.subject_id = e.subject_id
    JOIN rooms      r  ON r.room_id = e.room_id
    WHERE e.teacher_id = ?
    ORDER BY e.weekday ASC, e.pair_no ASC, g.name ASC
  });
  $sth->execute($teacher_id);

  my @rows;
  while (my $r = $sth->fetchrow_hashref) {
    push @rows, $r;
  }
  return \@rows;
}

my $cgi = CGI->new;

my $q       = dec_param($cgi, "q");
my $teacher = dec_param($cgi, "teacher");

# Мини-санитария: если слишком длинно, режем (чтобы в логах не было цирка)
$q = substr($q, 0, 100) if length($q) > 100;
$teacher = substr($teacher, 0, 100) if length($teacher) > 100;

my $dbh = db_connect();

my $teacher_row = ($teacher ne "") ? resolve_teacher($dbh, $teacher) : undef;

my $title = "Поиск преподавателя";
$title = "Занятия — " . esc($teacher_row->{name}) if $teacher_row;

html_header($title);

my $hero_text = ($teacher_row)
  ? ("Выбран преподаватель: <b>" . esc($teacher_row->{name}) . "</b>.")
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

# --------- 1) Стадия поиска: teacher ещё не выбран ---------
if (!$teacher_row) {
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

  my $teachers = find_teachers_by_query($dbh, $q);

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
    # ВАЖНО: передаём teacher_id, а не имя (так стабильнее)
    my $link = "/cgi-bin/teacher.cgi?q=" . urlenc($q) . "&teacher=" . urlenc($t->{teacher_id});
    print qq{
      <tr>
        <td>} . esc($t->{name}) . qq{</td>
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

# --------- 2) Стадия просмотра нагрузки выбранного преподавателя ---------
my $load = get_teacher_load($dbh, $teacher_row->{teacher_id});

if (!@$load) {
  print qq{
    <p>Для преподавателя <b>} . esc($teacher_row->{name}) . qq{</b> в расписании нет записей.</p>
    <p class="muted">Проверьте заполнение schedule_entries.</p>
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
  <p>Ниже показаны занятия преподавателя <b>} . esc($teacher_row->{name}) . qq{</b> по текущему расписанию.</p>
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
          <th>Примечание</th>
        </tr>
};

for my $r (@$load) {
  my $wd  = int($r->{weekday} || 0);
  my $day = $weekday_name{$wd} || "—";

  print qq{
        <tr>
          <td>} . esc($day) . qq{</td>
          <td>} . esc($r->{pair_no}) . qq{</td>
          <td>} . esc($r->{time}) . qq{</td>
          <td>} . esc($r->{group_name}) . qq{</td>
          <td>} . esc($r->{subject}) . qq{</td>
          <td>} . esc($r->{room}) . qq{</td>
          <td>} . esc($r->{note}) . qq{</td>
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
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
      alert("Подсказка:\\nВыберите сотрудника на странице «Часы приёма».\\n\\nКнопки: «Скопировать» копирует данные в буфер, «Печать» открывает окно печати.");
    }

    async function copyReception() {
      const root = document.getElementById("reception-root");
      if (!root) { alert("Не найден блок данных."); return; }

      let out = "";
      const dayCards = root.querySelectorAll("[data-day]");
      dayCards.forEach(card => {
        const day = card.getAttribute("data-day") || "";
        out += day + "\\n";

        const rows = card.querySelectorAll("table tr");
        rows.forEach((tr, idx) => {
          if (idx === 0) return;
          const tds = tr.querySelectorAll("td");
          const line = Array.from(tds).map(td => td.textContent.trim()).join(" | ");
          if (line) out += "  " + line + "\\n";
        });

        out += "\\n";
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

sub get_person {
  my ($pid) = @_;
  my $rows = Db::find_by("$data/reception_people.db", "person_id", $pid);
  return undef if !@$rows;
  return $rows->[0];
}

sub get_hours_rows {
  my ($pid) = @_;
  my $rows = Db::find_by("$data/reception_hours.db", "person_id", $pid);

  my @sorted = sort {
    ($a->{weekday} <=> $b->{weekday}) ||
    (($a->{time}||"") cmp ($b->{time}||""))
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
my $person_id = $q->param("person_id") // "";
$person_id =~ s/\s+//g;

my $person = $person_id ? get_person($person_id) : undef;
my $title = $person ? ("Часы приёма — " . esc($person->{short})) : "Часы приёма";

html_header($title);

my $hero_text = $person
  ? ("Выбран сотрудник: <b>" . esc($person->{short}) . "</b>.")
  : "Выберите сотрудника на странице часов приёма, чтобы увидеть расписание.";

print qq{
  <section class="hero" aria-label="Первый экран">
    <div class="hero-inner">
      <div>
        <h1>Часы приёма</h1>
        <p>$hero_text</p>

        <div class="hero-actions">
          <a class="btn primary" href="/www/reception.html">Сменить сотрудника</a>
          <a class="btn" href="#content">К результату</a>
          <a class="btn" href="/www/index.html">На главную</a>

          <!-- обычная кнопка с картинкой (как у тебя уже сделано в расписании) -->
          <button type="button" class="btn" onclick="location.href='/www/reception.html'"
                  style="display:inline-flex;align-items:center;gap:8px">
            К выбору
          </button>

          <!-- JS-кнопки -->
          <button type="button" class="btn" onclick="showHelp()">Справка</button>
          <button type="button" class="btn" onclick="copyReception()">Скопировать</button>
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

if (!$person_id) {
  print qq{
    <p>Сотрудник не выбран. Вернитесь на страницу часов приёма и выберите сотрудника.</p>
    <p style="margin-top:12px">
      <a class="btn primary" href="/www/reception.html">Выбрать сотрудника</a>
      <a class="btn" href="/www/index.html">На главную</a>
      <a class="btn" href="#top">Наверх</a>
    </p>
  };
  print qq{</div></section>};
  html_footer();
  exit;
}

if (!$person) {
  print qq{
    <p>Неизвестный сотрудник: <b>} . esc($person_id) . qq{</b>.</p>
    <p class="muted">Проверьте выбор и повторите попытку.</p>
    <p style="margin-top:12px">
      <a class="btn primary" href="/www/reception.html">Выбрать сотрудника</a>
      <a class="btn" href="#top">Наверх</a>
    </p>
  };
  print qq{</div></section>};
  html_footer();
  exit;
}

my $rows = get_hours_rows($person_id);

print qq{
  <p><b>} . esc($person->{name}) . qq{</b></p>
  <p class="muted">} . esc($person->{role}) . qq{</p>
  <p class="muted">Контакты: } . esc($person->{phone}) . qq{ · } . esc($person->{email}) . qq{</p>
  <p style="margin-top:12px">
    <a class="btn" href="/www/reception.html">Сменить сотрудника</a>
    <a class="btn" href="#top">Наверх</a>
    <a class="btn" href="#bottom">В конец</a>
  </p>
</div></section>
};

if (!@$rows) {
  print qq{
    <section class="card" style="margin-top:16px">
      <div class="card-header"><h2>Данные</h2></div>
      <div class="card-body">
        <p>Для выбранного сотрудника часы приёма пока не заполнены.</p>
      </div>
    </section>
  };
  html_footer();
  exit;
}

my $by = group_by_weekday($rows);

print qq{<div id="reception-root">};

for my $wd (1..6) {
  my $day_rows = $by->{$wd} || [];
  next if !@$day_rows; 

  my $day_title = $weekday_name{$wd};

  print qq{
    <article class="card" id="day$wd" data-day="$day_title" style="margin-top:16px">
      <div class="card-header"><h2>} . esc($day_title) . qq{</h2></div>
      <div class="card-body">
        <table>
          <tr>
            <th>Время</th>
            <th>Примечание</th>
          </tr>
  };

  for my $r (@$day_rows) {
    print qq{
          <tr>
            <td>} . esc($r->{time}) . qq{</td>
            <td>} . esc($r->{note}) . qq{</td>
          </tr>
    };
  }

  print qq{
        </table>
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
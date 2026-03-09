#!/usr/bin/perl
use strict;
use warnings;
use utf8;
use CGI qw(:standard);
use FindBin qw($Bin);
use lib $Bin;

use db;

my $dbh = Db::connect_sqlite(db_path => "$Bin/data/site.sqlite");

print header(-charset => 'UTF-8');
print start_html(
    -title => 'Часы приёма деканата',
    -style => { -src => '/www/style.css' }
);

my $staff_list = $dbh->selectall_arrayref(
    "SELECT staff_id, name, position FROM staff WHERE is_teacher = 0 ORDER BY staff_id",
    { Slice => {} }
);

my $person_id = param('person_id');

print <<'HTML';
<header>
  <nav>
    <a href="/cgi-bin/index.cgi">Главная</a>
    <a href="/cgi-bin/history.cgi">История</a>
    <a href="/cgi-bin/departments.cgi">Кафедры</a>
    <a href="/cgi-bin/schedule.cgi">Расписание</a>
    <a href="/cgi-bin/reception.cgi">Часы приёма</a>
    <a href="/cgi-bin/teacher.cgi">Преподаватели</a>
    <a href="/cgi-bin/statistics.cgi">Статистика</a>
    <a href="/cgi-bin/staff_reception.cgi">Приём задолжностей</a>
    <a href="/cgi-bin/program_subjects.cgi">Дисциплины программы</a>
  </nav>
</header>

<div class="container">
  <a id="top"></a>

  <section class="hero">
    <div class="hero-inner">
      <div>
        <h1>Часы приёма декана и заместителей декана</h1>
        <p>Выберите сотрудника и нажмите кнопку, чтобы увидеть часы приёма.</p>
      </div>
    </div>
  </section>

  <section class="card" id="form" style="margin-top:16px">
    <div class="card-header"><h2>Выбор сотрудника</h2></div>
    <div class="card-body">
      <form method="GET" action="/cgi-bin/reception.cgi">
        <label>Сотрудник:
          <select name="person_id" required>
            <option value="">-- выбрать --</option>
HTML

for my $s (@$staff_list) {
    my $selected = ($person_id && $s->{staff_id} == $person_id) ? 'selected' : '';
    print qq{<option value="$s->{staff_id}" $selected>$s->{name} ($s->{position})</option>\n};
}

print <<'HTML';
          </select>
        </label>
        <p style="margin-top:12px">
          <input class="btn primary" type="submit" value="Показать часы приёма">
          <a class="btn" href="#top">Наверх</a>
        </p>
      </form>
    </div>
  </section>
HTML

if ($person_id) {

    my $sql = q{
        SELECT weekday, time
        FROM reception_hours
        WHERE staff_id = ?
        ORDER BY weekday, time
    };
    my $hours = $dbh->selectall_arrayref($sql, { Slice => {} }, $person_id);

    my @weekdays = qw(Понедельник Вторник Среда Четверг Пятница Суббота Воскресенье);

    print qq{
  <section class="card" style="margin-top:16px">
    <div class="card-header"><h2>Часы приёма</h2></div>
    <div class="card-body">
};

    if (@$hours) {
        print "<table>\n<tr><th>День недели</th><th>Время</th></tr>\n";
        for my $h (@$hours) {
            my $day_name = $weekdays[$h->{weekday}-1];
            print qq{<tr><td>$day_name</td><td>$h->{time}</td></tr>\n};
        }
        print "</table>\n";
    } else {
        print "<p>Часы приёма для выбранного сотрудника пока не заданы.</p>\n";
    }

    print "</div></section>\n";
}

print <<'HTML';
</div>

<div class="footer">
  © Факультет вычислительной техники
</div>
HTML

print end_html;
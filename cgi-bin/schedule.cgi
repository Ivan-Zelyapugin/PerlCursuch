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
    -title => 'Расписание',
    -style => { -src => '/www/style.css' }
);

my $groups = $dbh->selectall_arrayref(
    "SELECT group_id, name FROM groups ORDER BY name",
    { Slice => {} }
);

my $group_id = param('group_id');

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
        <h1>Расписание занятий</h1>
        <p>Выберите учебную группу и получите актуальное расписание.</p>
      </div>
    </div>
  </section>

  <section class="card" id="form" style="margin-top:16px">
    <div class="card-header"><h2>Выбор группы</h2></div>
    <div class="card-body">
      <form method="GET" action="/cgi-bin/schedule.cgi">
        <label>Группа:
          <select name="group_id" required>
            <option value="">-- выбрать --</option>
HTML

for my $g (@$groups) {
    my $selected = ($group_id && $g->{group_id} == $group_id) ? 'selected' : '';
    print qq{<option value="$g->{group_id}" $selected>$g->{name}</option>\n};
}

print <<'HTML';
          </select>
        </label>
        <p style="margin-top:12px">
          <input class="btn primary" type="submit" value="Показать расписание">
          <a class="btn" href="#top">Наверх</a>
        </p>
      </form>
    </div>
  </section>
HTML

if ($group_id) {

    my $sql = q{
        SELECT
            s.weekday,
            ts.pair_no,
            ts.time,
            subj.name AS subject,
            st.name AS teacher,
            r.name AS room
        FROM schedule s
        JOIN time_slots ts ON s.slot_id = ts.slot_id
        JOIN subjects subj ON s.subject_id = subj.subject_id
        JOIN staff st ON s.teacher_id = st.staff_id
        JOIN rooms r ON s.room_id = r.room_id
        WHERE s.group_id = ?
        ORDER BY s.weekday, ts.pair_no
    };
    my $rows = $dbh->selectall_arrayref($sql, { Slice => {} }, $group_id);

    print qq{
  <section class="card" style="margin-top:16px">
    <div class="card-header"><h2>Расписание группы</h2></div>
    <div class="card-body">
};

    my %by_day;
    for my $r (@$rows) {
        push @{$by_day{$r->{weekday}}}, $r;
    }

    for my $day (1..7) {
        next unless exists $by_day{$day};
        print qq{<h3>День $day</h3>\n<table>\n<tr><th>№ пары</th><th>Время</th><th>Дисциплина</th><th>Преподаватель</th><th>Аудитория</th></tr>\n};
        for my $r (@{$by_day{$day}}) {
            print qq{
<tr>
  <td>$r->{pair_no}</td>
  <td>$r->{time}</td>
  <td>$r->{subject}</td>
  <td>$r->{teacher}</td>
  <td>$r->{room}</td>
</tr>
            };
        }
        print "</table>\n";
    }

    print "</div></section>\n";
}

print <<'HTML';
  <a id="bottom"></a>
</div>

<div class="footer">
  © Факультет вычислительной техники
</div>
HTML

print end_html;
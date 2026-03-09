#!/usr/bin/perl
use strict;
use warnings;
use utf8;
use CGI qw(:standard);
use FindBin qw($Bin);
use lib $Bin;
use db;

my $dbh = Db::connect_sqlite(db_path => "$Bin/data/site.sqlite");

my %weekday_name = (
  1 => "Понедельник",
  2 => "Вторник",
  3 => "Среда",
  4 => "Четверг",
  5 => "Пятница",
  6 => "Суббота",
  7 => "Воскресенье",
);

sub esc { my $s = shift // ''; $s =~ s/&/&amp;/g; $s =~ s/</&lt;/g; $s =~ s/>/&gt;/g; $s =~ s/"/&quot;/g; $s }

my $teacher_id = param('teacher') || '';
my $q          = param('q') || '';

my $teachers = $dbh->selectall_arrayref(
    "SELECT staff_id, name FROM staff WHERE is_teacher = 1 ORDER BY name",
    { Slice => {} }
);

my $teacher_row;
if ($teacher_id) {
    ($teacher_row) = grep { $_->{staff_id} == $teacher_id } @$teachers;
}

print "Content-Type: text/html; charset=UTF-8\n\n";
print <<'HTML';
<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Преподаватели</title>
<link rel="stylesheet" href="/www/style.css">
</head>
<body>
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
<section class="card">
<div class="card-header"><h2>Выбор преподавателя</h2></div>
<div class="card-body">
<form method="GET" action="/cgi-bin/teacher.cgi">
<label>Преподаватель:
<select name="teacher" required>
<option value="">-- выбрать --</option>
HTML

for my $t (@$teachers) {
    my $sel = ($teacher_row && $t->{staff_id} == $teacher_row->{staff_id}) ? 'selected' : '';
    print qq{<option value="$t->{staff_id}" $sel>} . esc($t->{name}) . "</option>\n";
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

if ($teacher_row) {
    my $schedule = $dbh->selectall_arrayref(q{
        SELECT s.weekday, ts.pair_no, ts.time, g.name AS group_name,
               sub.name AS subject_name, r.name AS room_name
        FROM schedule s
        JOIN time_slots ts ON ts.slot_id = s.slot_id
        JOIN groups g ON g.group_id = s.group_id
        JOIN subjects sub ON sub.subject_id = s.subject_id
        JOIN rooms r ON r.room_id = s.room_id
        WHERE s.teacher_id = ?
        ORDER BY s.weekday, ts.pair_no, g.name
    }, { Slice => {} }, $teacher_row->{staff_id});

    print qq{
<section class="card" style="margin-top:16px">
<div class="card-header"><h2>Расписание преподавателя: } . esc($teacher_row->{name}) . qq{</h2></div>
<div class="card-body">
};

    if (@$schedule) {
        print qq{<table>
<tr><th>День</th><th>Пара</th><th>Время</th><th>Группа</th><th>Дисциплина</th><th>Аудитория</th></tr>
};

        my %seen;  
        for my $r (@$schedule) {
            my $key = "$r->{weekday}-$r->{pair_no}";
            next if $seen{$key}++; 

            my $day = $weekday_name{$r->{weekday}} // '—';
            print qq{
<tr>
<td>} . esc($day) . qq{</td>
<td>} . esc($r->{pair_no}) . qq{</td>
<td>} . esc($r->{time}) . qq{</td>
<td>} . esc($r->{group_name}) . qq{</td>
<td>} . esc($r->{subject_name}) . qq{</td>
<td>} . esc($r->{room_name}) . qq{</td>
</tr>
};
        }

        print "</table>\n";
    } else {
        print "<p>Для преподавателя нет записей в расписании.</p>\n";
    }

    print qq{
<p style="margin-top:12px">
<a class="btn" href="#top">Наверх</a>
</p>
</div></section>
};
}

print <<'HTML';
<div class="footer">
© Факультет вычислительной техники
</div>
</div>
</body>
</html>
HTML
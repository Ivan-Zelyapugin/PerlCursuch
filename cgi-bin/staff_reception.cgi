#!/usr/bin/perl
use strict;
use warnings;
use utf8;
use FindBin qw($Bin);
use lib $Bin;
use db;

my $dbh = Db::connect_sqlite(db_path => "$Bin/data/site.sqlite");

sub esc {
    my $s = shift // '';
    $s =~ s/&/&amp;/g;
    $s =~ s/</&lt;/g;
    $s =~ s/>/&gt;/g;
    $s =~ s/"/&quot;/g;
    return $s;
}

my %weekday_name = (
  1 => "Понедельник",
  2 => "Вторник",
  3 => "Среда",
  4 => "Четверг",
  5 => "Пятница",
  6 => "Суббота",
  7 => "Воскресенье",
);

print "Content-Type: text/html; charset=UTF-8\n\n";

print <<'HTML';
<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Часы приёма сотрудников</title>
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

<section class="card">
<div class="card-header"><h2>Часы приёма сотрудников</h2></div>
<div class="card-body">

<p>Ниже указаны пары, в которые преподаватели свободны от занятий и могут проводить приём студентов.</p>

HTML

my $staff = $dbh->selectall_arrayref(q{
    SELECT staff_id, name, position
    FROM staff
    WHERE is_teacher = 1
    ORDER BY name
}, { Slice => {} });

my $slots = $dbh->selectall_arrayref(q{
    SELECT slot_id, pair_no, time
    FROM time_slots
    ORDER BY pair_no
}, { Slice => {} });

for my $person (@$staff) {

    print "<h3>" . esc($person->{name}) . " — " . esc($person->{position}) . "</h3>";

    print "<table>";
    print "<tr><th>День</th><th>Пара</th><th>Время</th></tr>";

    for my $day (1..5) {

        for my $slot (@$slots) {

            my ($busy) = $dbh->selectrow_array(q{
                SELECT COUNT(*)
                FROM schedule
                WHERE teacher_id = ?
                AND weekday = ?
                AND slot_id = ?
            }, undef, $person->{staff_id}, $day, $slot->{slot_id});

            if (!$busy) {

                print "<tr>";
                print "<td>" . $weekday_name{$day} . "</td>";
                print "<td>" . esc($slot->{pair_no}) . "</td>";
                print "<td>" . esc($slot->{time}) . "</td>";
                print "</tr>";

            }
        }
    }

    print "</table><br>";
}

print <<'HTML';
<p style="margin-top:12px">
<a class="btn" href="/cgi-bin/index.cgi">На главную</a>
</p>

</div>
</section>

<div class="footer">
© Факультет вычислительной техники
</div>

</div>
</body>
</html>
HTML
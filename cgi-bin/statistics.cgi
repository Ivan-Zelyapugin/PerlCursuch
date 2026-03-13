#!/usr/bin/perl
use strict;
use warnings;
use utf8;
use FindBin qw($Bin);
use lib $Bin;
use db;

my $dbh = Db::connect_sqlite(db_path => "$Bin/data/site.sqlite");

# ------------------------- Заголовки -------------------------
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

print "Content-Type: text/html; charset=UTF-8\n\n";
print <<'HTML';
<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Статистика кафедр</title>
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

<div class="fab-nav" aria-label="Быстрая навигация">
  <a class="fab" href="#top" title="В начало">↑</a>
  <a class="fab" href="#bottom" title="В конец">↓</a>
</div>

<div class="container">
<a id="top"></a>
<section class="card">
<div class="card-header"><h2>Статистика кафедр и программ</h2></div>
<div class="card-body">
<p>На этой странице показана статистика по кафедрам факультета: количество направлений подготовки, групп, преподавателей и административного персонала.</p>
HTML

my $sql = q{
    SELECT 
        d.department_id,
        d.name AS department_name,
        COUNT(DISTINCT p.program_id) AS programs_count,
        COUNT(DISTINCT g.group_id) AS groups_count,
        COUNT(DISTINCT CASE WHEN s.is_teacher=1 THEN s.staff_id END) AS teachers_count,
        COUNT(DISTINCT CASE WHEN s.is_teacher=0 THEN s.staff_id END) AS staff_count
    FROM departments d
    LEFT JOIN programs p ON p.department_id = d.department_id
    LEFT JOIN groups g ON g.program_id = p.program_id
    LEFT JOIN staff s ON s.faculty_id = d.faculty_id
    GROUP BY d.department_id
    ORDER BY d.name
};

my $stats = $dbh->selectall_arrayref($sql, { Slice => {} });

if (@$stats) {
    print qq{
<table>
<tr>
<th>Кафедра</th>
<th>Направления</th>
<th>Группы</th>
<th>Преподаватели</th>
<th>Административный персонал</th>
</tr>
};
    for my $row (@$stats) {
        print qq{
<tr>
<td><a href="/cgi-bin/departments.cgi#$row->{department_id}">} . esc($row->{department_name}) . qq{</a></td>
<td>} . esc($row->{programs_count}) . qq{</td>
<td>} . esc($row->{groups_count}) . qq{</td>
<td>} . esc($row->{teachers_count}) . qq{</td>
<td>} . esc($row->{staff_count}) . qq{</td>
</tr>
};
    }
    print "</table>\n";
} else {
    print "<p>Данные отсутствуют.</p>\n";
}

print <<'HTML';
<p style="margin-top:12px">
<a class="btn" href="#top">Наверх</a>
<a class="btn" href="/cgi-bin/index.cgi">На главную</a>
</p>
</div>

<a id ="bottom"></a>

</section>
<div class="footer">
© Факультет вычислительной техники
</div>
</div>
</body>
</html>
HTML
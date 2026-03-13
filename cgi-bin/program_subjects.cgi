#!/usr/bin/perl
use strict;
use warnings;
use utf8;

use FindBin qw($Bin);
use lib $Bin;

use CGI qw(:standard);
use db;

my $dbh = Db::connect_sqlite(db_path => "$Bin/data/site.sqlite");

sub esc { my $s = shift // ''; $s =~ s/&/&amp;/g; $s =~ s/</&lt;/g; $s =~ s/>/&gt;/g; $s =~ s/"/&quot;/g; $s }

my $program_id = param('program') || '';

# Получаем все программы для выпадающего списка
my $programs = $dbh->selectall_arrayref(
    "SELECT p.program_id, p.code, p.name, d.name AS department_name
     FROM programs p
     JOIN departments d ON d.department_id = p.department_id
     ORDER BY d.name, p.code",
    { Slice => {} }
);

# Получаем список дисциплин выбранной программы (только по одному преподавателю)
my $subjects = [];
if ($program_id) {
    $subjects = $dbh->selectall_arrayref(q{
        SELECT
            subj.name AS subject_name,
            st.name AS teacher_name
        FROM programs p
        JOIN groups g ON g.program_id = p.program_id
        JOIN schedule s ON s.group_id = g.group_id
        JOIN subjects subj ON subj.subject_id = s.subject_id
        JOIN staff st ON st.staff_id = s.teacher_id
        WHERE p.program_id = ?
        GROUP BY subj.subject_id
        ORDER BY subj.name
    }, { Slice => {} }, $program_id);
}

print "Content-Type: text/html; charset=UTF-8\n\n";

print <<'HTML';
<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Дисциплины программы</title>
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
<a href="/cgi-bin/teachers.cgi">Преподаватели</a>
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
<div class="card-header"><h2>Выбор программы</h2></div>
<div class="card-body">
<form method="GET" action="/cgi-bin/program_subjects.cgi">
<label>Программа:
<select name="program" required>
<option value="">-- выбрать --</option>
HTML

for my $p (@$programs) {
    my $sel = ($program_id && $p->{program_id} == $program_id) ? 'selected' : '';
    print qq{<option value="$p->{program_id}" $sel>} . esc($p->{department_name}) . " — $p->{code} — " . esc($p->{name}) . "</option>\n";
}

print <<'HTML';
</select>
</label>
<p style="margin-top:12px">
<input class="btn primary" type="submit" value="Показать дисциплины">
<a class="btn" href="#top">Наверх</a>
</p>
</form>
</div>
</section>
HTML

if ($program_id) {
    print qq{
<section class="card" style="margin-top:16px">
<div class="card-header"><h2>Дисциплины выбранной программы</h2></div>
<div class="card-body">
};

    if (@$subjects) {
        print qq{<table>
<tr><th>Дисциплина</th><th>Преподаватель</th></tr>
};
        for my $s (@$subjects) {
            print qq{
<tr>
<td>} . esc($s->{subject_name}) . qq{</td>
<td>} . esc($s->{teacher_name}) . qq{</td>
</tr>
};
        }
        print "</table>\n";
    } else {
        print "<p>Для выбранной программы дисциплины не найдены.</p>\n";
    }

    print qq{
<p style="margin-top:12px">
<a class="btn" href="#top">Наверх</a>
</p>
</div>

<a id ="bottom"></a>

</section>
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
#!/usr/bin/perl
use strict;
use warnings;
use utf8;

use FindBin qw($Bin);
use lib $Bin;

use db;

my $data_dir = "$Bin/data";
my $db_path  = "$data_dir/site.sqlite";

my $dbh = Db::connect_sqlite(db_path => $db_path);

my $sql_depts = q{
    SELECT
        department_id,
        name,
        short_name,
        address,
        phone,
        email,
        description
    FROM departments
    ORDER BY name
};
my $departments = $dbh->selectall_arrayref($sql_depts, { Slice => {} });

my $sql_programs = q{
    SELECT program_id, department_id, code, name
    FROM programs
    ORDER BY code
};
my $programs = $dbh->selectall_arrayref($sql_programs, { Slice => {} });

my %programs_for_dept;
for my $p (@$programs) {
    push @{$programs_for_dept{$p->{department_id}}}, $p;
}

print "Content-Type: text/html; charset=UTF-8\n\n";

print <<'HTML';
<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Кафедры</title>
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

<h1>Кафедры факультета</h1>

<section class="card">

<div class="card-header">
<h2>Список кафедр</h2>
</div>

<div class="card-body">

<table>
<tr>
<th>Кафедра</th>
<th>Телефон</th>
<th>Email</th>
</tr>
HTML

for my $d (@$departments) {
    print qq{
<tr>
<td><a href="#dept$d->{department_id}">$d->{short_name}</a></td>
<td>$d->{phone}</td>
<td>$d->{email}</td>
</tr>
};
}

print <<'HTML';
</table>

</div>
</section>

<section class="grid" style="margin-top:16px">
HTML

for my $d (@$departments) {
    print qq{
<article class="card" id="dept$d->{department_id}">

<div class="card-header">
<h2>$d->{name}</h2>
</div>

<div class="card-body">

<p>$d->{description}</p>

<p><b>Адрес:</b> $d->{address}</p>
<p><b>Телефон:</b> $d->{phone}</p>
<p><b>Email:</b> $d->{email}</p>
};

    if (exists $programs_for_dept{$d->{department_id}}) {
        print qq{<p><b>Направления подготовки:</b></p><ul>};
        for my $p (@{$programs_for_dept{$d->{department_id}}}) {
            print qq{<li>$p->{code} – $p->{name}</li>};
        }
        print "</ul>";
    }

    print qq{
<p style="margin-top:12px">
<a class="btn" href="#top">Наверх</a>
</p>

</div>
</article>
};
}

print <<'HTML';
</section>

</div>

<div class="footer">
© Факультет вычислительной техники
</div>

</body>
</html>
HTML
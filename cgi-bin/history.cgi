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

my $sql = q{
    SELECT name, history
    FROM faculties
    LIMIT 1
};

my $row = $dbh->selectrow_hashref($sql);

print "Content-Type: text/html; charset=UTF-8\n\n";

print <<"HTML";
<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>История факультета</title>
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

<h1>$row->{name}</h1>

<section class="card">

<div class="card-header">
<h2>История факультета</h2>
</div>

<div class="card-body">

<p>
$row->{history}
</p>

</div>

</section>

<a id ="bottom"></a>

</div>

<div class="footer">
© Факультет вычислительной техники
</div>

</body>
</html>
HTML
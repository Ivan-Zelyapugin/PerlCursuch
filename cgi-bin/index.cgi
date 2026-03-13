#!/usr/bin/perl
use strict;
use warnings;
use utf8;

use CGI qw(:standard);
use FindBin qw($Bin);
use lib $Bin;

use db;

print header(-type => "text/html", -charset => "utf-8");

my $dbh = Db::connect_sqlite(
    db_path => "$Bin/data/site.sqlite"
);

my $faculty = $dbh->selectrow_hashref(q{
    SELECT name, description, phone, email
    FROM faculties
    WHERE short_name = 'ФВТ'
});

my $programs = $dbh->selectall_arrayref(q{
    SELECT code, name
    FROM programs
    ORDER BY name
}, { Slice => {} });

print <<HTML;
<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>$faculty->{name}</title>
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

<section class="hero">
<div class="hero-inner">

<div>
<h1>$faculty->{name}</h1>
<p>$faculty->{description}</p>
</div>

<div class="hero-media">
<img src="/www/img/pgu_2.png" alt="Корпус университета">
</div>

</div>
</section>

<section class="grid" style="margin-top:16px">

<article class="card">
<div class="card-header"><h2>О факультете</h2></div>
<div class="card-body">

<p>
Факультет вычислительной техники готовит специалистов в области разработки
программного обеспечения, информационных систем и эксплуатации вычислительной
инфраструктуры.
</p>

<img src="/www/img/auditor.png" style="max-width:100%;border-radius:12px;">

</div>
</article>

<aside class="card">
<div class="card-header"><h2>Направления</h2></div>
<div class="card-body">
<ul class="list">
HTML

for my $p (@$programs) {
    print "<li>$p->{code} $p->{name}</li>";
}

print <<HTML;
</ul>
</div>
</aside>

</section>

<section class="card" style="margin-top:16px">

<div class="card-header"><h2>Контакты</h2></div>

<div class="card-body">

<table class="contact-table">

<tr>
<th>Телефон</th>
<td>$faculty->{phone}</td>
</tr>

<tr>
<th>Email</th>
<td><a href="mailto:$faculty->{email}">$faculty->{email}</a></td>
</tr>

</table>

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
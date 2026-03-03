#!/usr/bin/perl
use strict;
use warnings;
use utf8;

use CGI qw(:standard escapeHTML);
use FindBin qw($Bin);
use lib $Bin;

use Db;
use Html;

binmode(STDOUT, ":encoding(UTF-8)");

my $q = CGI->new;
my $dept_id = $q->param("dept_id") // "";

my $data = "$Bin/data";

print Html::page_begin(title => "Кафедра");

print "<h1>Кафедра</h1>";

print "<form method='GET' action='/cgi/department.cgi'>
  <label>Dept ID:
    <input name='dept_id' value='" . escapeHTML($dept_id) . "'>
  </label>
  <input type='submit' value='Показать'>
</form>";

print "<p>" . Html::img_button(href => "/departments.html", src => "/img/logo.png", alt => "Назад") . "</p>";

print "<button type='button' onclick='jsBtn()'>JS кнопка</button>";

if ($dept_id !~ /^\d+$/) {
    print "<p>Нужен числовой dept_id. Сейчас: <b>" . escapeHTML($dept_id) . "</b></p>";
    print Html::page_end();
    exit;
}

my $dept = Db::get_row("$data/departments.db", $dept_id);
if (!$dept) {
    print "<p>Кафедра не найдена: dept_id=$dept_id.</p>";
    print Html::page_end();
    exit;
}

print "<h2>" . escapeHTML($dept->{name}) . "</h2>";
print "<p><b>Телефон:</b> " . escapeHTML($dept->{phone}) . "</p>";
print "<p>" . escapeHTML($dept->{about}) . "</p>";

my $groups = Db::find_by("$data/groups.db", "dept_id", $dept_id);

print "<h3>Группы кафедры</h3>";
if (!@$groups) {
    print "<p>Групп нет.</p>";
} else {
    print "<ul>";
    for my $g (sort { $a->{group_id} <=> $b->{group_id} } @$groups) {
        my $gid = $g->{group_id};
        my $name = $g->{name};
        print "<li>" . escapeHTML($name) .
              " (ID: " . escapeHTML($gid) . ") " .
              "<a href='/cgi/schedule.cgi?group_id=" . escapeHTML($gid) . "'>Расписание</a></li>";
    }
    print "</ul>";
}

print Html::page_end();
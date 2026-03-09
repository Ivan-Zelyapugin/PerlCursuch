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

Db::txn($dbh, sub {
    $dbh->do("DELETE FROM programs");

    # Получаем ID кафедр по коротким названиям
    my %dept_id_for_short;
    my $sth = $dbh->prepare("SELECT department_id, short_name FROM departments");
    $sth->execute();
    while (my $row = $sth->fetchrow_hashref) {
        $dept_id_for_short{$row->{short_name}} = $row->{department_id};
    }

    my @programs = (
        { code => "09.03.01", name => "Информатика и вычислительная техника", dept_short => "ВТ" },
        { code => "09.03.01", name => "Системы автоматизированного проектирования", dept_short => "САПР" },
        { code => "09.03.02", name => "Информационные системы и технологии", dept_short => "МОиПЭВМ" },
        { code => "09.03.04", name => "Программная инженерия", dept_short => "МОиПЭВМ" },
        { code => "09.03.03", name => "Прикладная информатика", dept_short => "ИВС" },
        { code => "02.03.03", name => "Математическое обеспечение и администрирование информационных систем", dept_short => "САПР" },
        { code => "46.03.02", name => "Документоведение и архивоведение", dept_short => "ИНОУП" },
        { code => "01.03.04", name => "Прикладная математика", dept_short => "ВиПМ" },
        { code => "01.03.02", name => "Прикладная математика и информатика", dept_short => "КТ" },
    );

    my $ins = $dbh->prepare(q{
        INSERT INTO programs (department_id, code, name)
        VALUES (?, ?, ?)
    });

    for my $p (@programs) {
        my $dept_id = $dept_id_for_short{$p->{dept_short}};
        next unless defined $dept_id; 

        $ins->execute($dept_id, $p->{code}, $p->{name});
    }
});

print "Programs initialized in SQLite: $db_path\n";
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

    $dbh->do("DELETE FROM groups");

    # Получаем program_id по названию программы
    my %program_id_for_name;
    my $sth = $dbh->prepare("SELECT program_id, name FROM programs");
    $sth->execute();
    while (my $row = $sth->fetchrow_hashref) {
        $program_id_for_name{$row->{name}} = $row->{program_id};
    }

    my @groups = (
        { name => "23ВА1", program_name => "Информатика и вычислительная техника" },
        { name => "23ВБ1", program_name => "Информатика и вычислительная техника" },
        { name => "23ВВИ1", program_name => "Прикладная информатика" },
        { name => "23ВВИ2", program_name => "Прикладная информатика" },
        { name => "23ВВиа1", program_name => "Прикладная информатика" },
        { name => "23ВВП1", program_name => "Программная инженерия" },
        { name => "23ВВС1", program_name => "Системы автоматизированного проектирования" },
        { name => "23ВГ1", program_name => "Информационные системы и технологии" },
        { name => "23ВД1", program_name => "Математическое обеспечение и администрирование информационных систем" },
        { name => "23ВИ1", program_name => "Документоведение и архивоведение" },
        { name => "23ВИ2", program_name => "Документоведение и архивоведение" },
        { name => "23ВОА1", program_name => "Прикладная математика" },
        { name => "23ВОЭ1", program_name => "Прикладная математика" },
        { name => "23ВП1", program_name => "Программная инженерия" },
        { name => "23ВП2", program_name => "Программная инженерия" },
        { name => "23ВФ1", program_name => "Прикладная математика и информатика" },
        { name => "23ВЭР1", program_name => "Прикладная математика и информатика" },
        { name => "23ВЭЭ1", program_name => "Прикладная математика и информатика" },
    );

    my $ins = $dbh->prepare(q{
        INSERT INTO groups (program_id, name)
        VALUES (?, ?)
    });

    for my $g (@groups) {
        my $pid = $program_id_for_name{$g->{program_name}};
        next unless defined $pid; 
        $ins->execute($pid, $g->{name});
    }
});

print "Groups initialized in SQLite: $db_path\n";
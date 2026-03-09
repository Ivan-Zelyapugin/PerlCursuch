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
    $dbh->do("DELETE FROM time_slots");

    my @times = (
        [1, "08:30-10:05"],
        [2, "10:15-11:50"],
        [3, "12:10-13:45"],
        [4, "14:00-15:35"],
        [5, "15:45-17:20"],
    );

    my $ins = $dbh->prepare(q{
        INSERT INTO time_slots (pair_no, time)
        VALUES (?, ?)
    });

    for my $t (@times) {
        $ins->execute($t->[0], $t->[1]);
    }
});

print "Time slots initialized in SQLite: $db_path\n";
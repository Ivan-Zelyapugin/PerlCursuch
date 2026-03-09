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
    $dbh->do("DELETE FROM rooms");

    my @rooms;

    push @rooms, map { "7Б$_" } (201..207);

    for my $floor (101,201,301,401) {
        push @rooms, map { "7А$_" } ($floor .. $floor+16);
    }

    my $ins = $dbh->prepare(q{
        INSERT INTO rooms (name)
        VALUES (?)
    });

    for my $r (@rooms) {
        $ins->execute($r);
    }
});

print "Rooms initialized in SQLite: $db_path\n";
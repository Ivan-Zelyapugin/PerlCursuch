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

my @people = (
    { name => "Фионова Людмила Римовна", person_id => 1 },
    { name => "Бычков Андрей Станиславович", person_id => 2 },
    { name => "Писарев Аркадий Петрович", person_id => 3 },
    { name => "Мойко Наталья Валентиновна", person_id => 4 },
    { name => "Катышева Марина Александровна", person_id => 5 },
);

my %hours = (
    1 => [ [1, "12:00-13:30"], [2, "13:15-13:45"], [4, "13:15-13:45"] ],
    2 => [ [1, "09:00-11:25"], [2, "13:15-15:00"], [3, "11:40-15:35"], [4, "13:15-15:00"], [1, "09:00-11:40; 13:15-15:00"] ], 
    3 => [ [1, "09:00-11:40"], [2, "09:00-11:30"], [3, "09:00-13:15"], [4, "09:00-11:40"], [5, "13:15-15:00"] ], 
    4 => [ [1, "09:00-13:15"], [2, "09:00-14:00"], [3, "11:40-14:00"], [4, "11:00-14:00"] ], 
    5 => [ [1, "11:00-12:00"] ], 
);

Db::txn($dbh, sub {
    $dbh->do("DELETE FROM reception_hours");

    my $ins_hours = $dbh->prepare(q{
        INSERT INTO reception_hours (staff_id, weekday, time)
        VALUES (?, ?, ?)
    });

    for my $p (@people) {
        # Получаем staff_id из новой таблицы staff
        my ($staff_id) = $dbh->selectrow_array(
            "SELECT staff_id FROM staff WHERE name = ?",
            undef,
            $p->{name}
        );

        next unless $staff_id; 

        for my $slot (@{$hours{$p->{person_id}}}) {
            my ($weekday, $time) = @$slot;
            $ins_hours->execute($staff_id, $weekday, $time);
        }
    }
});

print "Reception hours initialized in SQLite: $db_path\n";
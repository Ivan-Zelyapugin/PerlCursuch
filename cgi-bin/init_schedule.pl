#!/usr/bin/perl
use strict;
use warnings;
use utf8;

use FindBin qw($Bin);
use lib $Bin;

use db;
use List::Util qw(shuffle);

my $data_dir = "$Bin/data";
my $db_path  = "$data_dir/site.sqlite";

my $dbh = Db::connect_sqlite(db_path => $db_path);

Db::txn($dbh, sub {
    $dbh->do("DELETE FROM schedule");

    # Получаем все id для ссылок
    my %group_ids;
    my $sth = $dbh->prepare("SELECT group_id, name FROM groups");
    $sth->execute();
    while (my $row = $sth->fetchrow_hashref) {
        $group_ids{$row->{name}} = $row->{group_id};
    }

    my %subject_ids;
    $sth = $dbh->prepare("SELECT subject_id, name FROM subjects");
    $sth->execute();
    while (my $row = $sth->fetchrow_hashref) {
        $subject_ids{$row->{name}} = $row->{subject_id};
    }

    my %teacher_ids;
    $sth = $dbh->prepare("SELECT staff_id, name FROM staff WHERE is_teacher=1");
    $sth->execute();
    while (my $row = $sth->fetchrow_hashref) {
        $teacher_ids{$row->{name}} = $row->{staff_id};
    }

    my %room_ids;
    $sth = $dbh->prepare("SELECT room_id, name FROM rooms");
    $sth->execute();
    while (my $row = $sth->fetchrow_hashref) {
        $room_ids{$row->{name}} = $row->{room_id};
    }

    my %slot_ids;
    $sth = $dbh->prepare("SELECT slot_id, pair_no FROM time_slots");
    $sth->execute();
    while (my $row = $sth->fetchrow_hashref) {
        $slot_ids{$row->{pair_no}} = $row->{slot_id};
    }

    my $ins = $dbh->prepare(q{
        INSERT INTO schedule
        (group_id, weekday, slot_id, subject_id, teacher_id, room_id)
        VALUES (?, ?, ?, ?, ?, ?)
    });

    # Для всех групп создаем расписание
    foreach my $group (keys %group_ids) {
        for my $weekday (1..5) { # понедельник-пятница
            for my $pair_no (1..5) { # все пары
                my $subject = (shuffle keys %subject_ids)[0];
                my $teacher = (shuffle keys %teacher_ids)[0];
                my $room    = (shuffle keys %room_ids)[0];

                $ins->execute(
                    $group_ids{$group},
                    $weekday,
                    $slot_ids{$pair_no},
                    $subject_ids{$subject},
                    $teacher_ids{$teacher},
                    $room_ids{$room}
                );
            }
        }
    }
});

print "Full schedule initialized in SQLite: $db_path\n";
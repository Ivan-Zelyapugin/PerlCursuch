#!/usr/bin/perl
use strict;
use warnings;
use utf8;

use FindBin qw($Bin);
use lib $Bin;

use db;

my $data_dir = "$Bin/data";
my $db_path  = "$data_dir/site.sqlite";
my $schema   = "$Bin/schema.sql";

my $dbh = Db::connect_sqlite(db_path => $db_path);
Db::exec_sql_file($dbh, $schema);

my %weekday_name = (
  1 => "Понедельник",
  2 => "Вторник",
  3 => "Среда",
  4 => "Четверг",
  5 => "Пятница",
  6 => "Суббота",
);

my @groups = (
  { group_id => 101, name => "24-ИС-1" },
  { group_id => 102, name => "24-ИС-2" },
  { group_id => 103, name => "24-ИТ-1" },
  { group_id => 104, name => "24-ВИ-1" },
  { group_id => 105, name => "24-ВП-1" },
);

my %track = (
  "ИС" => {
    subjects => ["Программирование", "Базы данных", "Веб-технологии", "Алгоритмы", "ОС", "Сети"],
    teachers => ["Иванов И.И.", "Петров П.П.", "Сидорова А.А.", "Кузнецов М.М."],
    rooms    => ["A-101", "A-202", "B-305", "B-112"],
  },
  "ИТ" => {
    subjects => ["Инфраструктура", "Администрирование", "Сети", "ОС", "Безопасность", "Проектирование ИС"],
    teachers => ["Орлов Д.Д.", "Зайцева Н.Н.", "Романенко В.В.", "Смирнов А.А."],
    rooms    => ["C-210", "C-114", "A-203", "B-120"],
  },
  "ВИ" => {
    subjects => ["Математика", "Линейная алгебра", "Дискретная математика", "Алгоритмы", "Теория вероятностей", "Матанализ"],
    teachers => ["Тында А.Н.", "Соколова Т.Т.", "Егоров Н.Н.", "Громова В.В."],
    rooms    => ["M-101", "M-205", "M-301", "A-110"],
  },
  "ВП" => {
    subjects => ["Физика", "Электроника", "Схемотехника", "ОС", "Архитектура ЭВМ", "Сети"],
    teachers => ["Борисов С.С.", "Мельников А.А.", "Лебедева И.И.", "Макаров К.К."],
    rooms    => ["P-201", "P-104", "A-115", "B-220"],
  },
);

sub detect_track {
  my ($group_name) = @_;
  return "ИС" if $group_name =~ /-ИС-/;
  return "ИТ" if $group_name =~ /-ИТ-/;
  return "ВИ" if $group_name =~ /-ВИ-/;
  return "ВП" if $group_name =~ /-ВП-/;
  return "ИС";
}

my @times = (
  [1, "08:30-10:05"],
  [2, "10:15-11:50"],
  [3, "12:10-13:45"],
);

Db::txn($dbh, sub {
    # подчистим расписание и справочники, если ты переинициализируешь
    $dbh->do("DELETE FROM schedule_entries");
    $dbh->do("DELETE FROM time_slots");
    $dbh->do("DELETE FROM groups");

    # time_slots
    my $ins_slot = $dbh->prepare("INSERT INTO time_slots (pair_no, time) VALUES (?, ?)");
    for my $t (@times) {
        $ins_slot->execute($t->[0], $t->[1]);
    }

    # groups
    my $ins_group = $dbh->prepare("INSERT INTO groups (group_id, name, track) VALUES (?, ?, ?)");
    for my $g (@groups) {
        my $tkey = detect_track($g->{name});
        $ins_group->execute($g->{group_id}, $g->{name}, $tkey);
    }

    # Готовим statement для расписания
    my $ins_entry = $dbh->prepare(q{
        INSERT INTO schedule_entries (group_id, weekday, pair_no, subject_id, teacher_id, room_id, note)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(group_id, weekday, pair_no) DO UPDATE SET
          subject_id=excluded.subject_id,
          teacher_id=excluded.teacher_id,
          room_id=excluded.room_id,
          note=excluded.note
    });

    my $rows = 0;

    for my $g (@groups) {
        my $gid   = $g->{group_id};
        my $gname = $g->{name};

        my $tkey = detect_track($gname);
        my $cfg  = $track{$tkey};

        for my $wd (1..6) {
            for my $pair_no (1..3) {
                my $si = ($gid + $wd + $pair_no) % scalar(@{$cfg->{subjects}});
                my $ti = ($gid + $wd * 2 + $pair_no) % scalar(@{$cfg->{teachers}});
                my $ri = ($gid + $wd * 3 + $pair_no) % scalar(@{$cfg->{rooms}});

                my $subject_name = $cfg->{subjects}->[$si];
                my $teacher_name = $cfg->{teachers}->[$ti];
                my $room_name    = $cfg->{rooms}->[$ri];

                my $subject_id = Db::id_for_unique_name($dbh, "subjects",  "subject_id", "name", $subject_name);
                my $teacher_id = Db::id_for_unique_name($dbh, "teachers",  "teacher_id", "name", $teacher_name);
                my $room_id    = Db::id_for_unique_name($dbh, "rooms",     "room_id",    "name", $room_name);

                $ins_entry->execute(
                    $gid,
                    $wd,
                    $pair_no,
                    $subject_id,
                    $teacher_id,
                    $room_id,
                    $weekday_name{$wd} // ""
                );

                $rows++;
            }
        }
    }

    print "Schedule initialized in SQLite: rows=$rows, db=$db_path\n";
});
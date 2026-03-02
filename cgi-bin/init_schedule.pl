#!/usr/bin/perl
use strict;
use warnings;
use utf8;

use FindBin qw($Bin);
use lib $Bin;

require "db.pm";

my $data = "$Bin/data";

unlink("$data/schedule.db");

my @groups = (
  { group_id => 101, name => "24-ИС-1" },
  { group_id => 102, name => "24-ИС-2" },
  { group_id => 103, name => "24-ИТ-1" },
  { group_id => 104, name => "24-ВИ-1" },
  { group_id => 105, name => "24-ВП-1" },
);

for my $g (@groups) {
  Db::put_row("$data/groups.db", $g->{group_id}, {
    group_id => $g->{group_id},
    name     => $g->{name},
  });
}

my @times = (
  "08:30-10:05",
  "10:15-11:50",
  "12:10-13:45",
);

my %weekday_name = (
  1 => "Понедельник",
  2 => "Вторник",
  3 => "Среда",
  4 => "Четверг",
  5 => "Пятница",
  6 => "Суббота",
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
  if ($group_name =~ /-ИС-/) { return "ИС"; }
  if ($group_name =~ /-ИТ-/) { return "ИТ"; }
  if ($group_name =~ /-ВИ-/) { return "ВИ"; }
  if ($group_name =~ /-ВП-/) { return "ВП"; }
  return "ИС";
}

my $row_id = 1;

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

      Db::put_row("$data/schedule.db", $row_id, {
        row_id   => $row_id,
        group_id => $gid,
        weekday  => $wd,                       
        pair_no  => $pair_no,                  
        time     => $times[$pair_no - 1],
        subject  => $cfg->{subjects}->[$si],
        teacher  => $cfg->{teachers}->[$ti],
        room     => $cfg->{rooms}->[$ri],
        note     => $weekday_name{$wd},         
      });

      $row_id++;
    }
  }
}

print "Schedule initialized: groups=5, days=6, pairs/day=3, rows=" . ($row_id - 1) . " in $data\n";
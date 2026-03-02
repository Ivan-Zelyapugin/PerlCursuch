#!/usr/bin/perl
use strict;
use warnings;
use utf8;

use FindBin qw($Bin);
use lib $Bin;

require "db.pm";

my $data = "$Bin/data";

unlink("$data/reception_people.db");
unlink("$data/reception_hours.db");

Db::put_row("$data/reception_people.db", 1, {
  person_id => 1,
  name  => "Фионова Людмила Римовна",
  short => "Фионова Л.Р.",
  role  => "Декан ФВТ",
  email => 'fvt@pnzgu.ru',
  phone => "+7 (8412) 66-65-60",
});

Db::put_row("$data/reception_people.db", 2, {
  person_id => 2,
  name  => "Бычков Андрей Станиславович",
  short => "Бычков А.С.",
  role  => "Заместитель декана по учебной работе",
  email => 'fvt@pnzgu.ru',
  phone => "+7 (8412) 66-65-60",
});

Db::put_row("$data/reception_people.db", 3, {
  person_id => 3,
  name  => "Писарев Аркадий Петрович",
  short => "Писарев А.П.",
  role  => "Заместитель декана по учебной работе",
  email => 'pisarev60@mail.ru',
  phone => "+7 (8412) 66-65-60",
});

Db::put_row("$data/reception_people.db", 4, {
  person_id => 4,
  name  => "Мойко Наталья Валентиновна",
  short => "Мойко Н.В.",
  role  => "Заместитель декана по учебной работе",
  email => 'fvt@pnzgu.ru',
  phone => "+7 (8412) 66-65-60",
});

Db::put_row("$data/reception_people.db", 5, {
  person_id => 5,
  name  => "Катышева Марина Александровна",
  short => "Катышева М.А.",
  role  => "Заместитель декана по молодежной политике и воспитательной деятельности",
  email => 'fvt@pnzgu.ru',
  phone => "+7 (8412) 66-65-60",
});

my $id = 1;

sub add_row {
  my (%r) = @_;
  $r{row_id} = $id++;
  Db::put_row("$data/reception_hours.db", $r{row_id}, \%r);
}

# Фионова Л.Р.
add_row(person_id => 1, weekday => 1, time => "12:00-13:30", note => "");
add_row(person_id => 1, weekday => 2, time => "13:15-13:45", note => "");
add_row(person_id => 1, weekday => 4, time => "13:15-13:45", note => "");

# Мойко Н.В.
add_row(person_id => 4, weekday => 1, time => "09:00-13:15", note => "");
add_row(person_id => 4, weekday => 2, time => "09:00-14:00", note => "");
add_row(person_id => 4, weekday => 3, time => "11:40-14:00", note => "I неделя");
add_row(person_id => 4, weekday => 4, time => "11:00-14:00", note => "II неделя");

# Бычков А.С.
add_row(person_id => 2, weekday => 1, time => "09:00-11:25", note => "I неделя");
add_row(person_id => 2, weekday => 2, time => "13:15-15:00", note => "I неделя");
add_row(person_id => 2, weekday => 3, time => "11:40-15:35", note => "по перерывам");
add_row(person_id => 2, weekday => 4, time => "13:15-15:00", note => "I неделя");
add_row(person_id => 2, weekday => 1, time => "09:00-11:40; 13:15-15:00", note => "II неделя");

# Писарев А.П.
add_row(person_id => 3, weekday => 1, time => "09:00-11:40", note => "I неделя; по перерывам");
add_row(person_id => 3, weekday => 2, time => "09:00-11:30", note => "I неделя");
add_row(person_id => 3, weekday => 3, time => "09:00-13:15", note => "I неделя; по перерывам");
add_row(person_id => 3, weekday => 4, time => "09:00-11:40", note => "II неделя");
add_row(person_id => 3, weekday => 5, time => "13:15-15:00", note => "II неделя");

# Катышева М.А.
add_row(person_id => 5, weekday => 1, time => "11:00-12:00", note => "");

print "Reception DB initialized in $data\n";
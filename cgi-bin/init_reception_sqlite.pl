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

Db::txn($dbh, sub {
    $dbh->do("DELETE FROM reception_hours");
    $dbh->do("DELETE FROM people");

    my @people = (
      {
        person_id => 1,
        name  => "Фионова Людмила Римовна",
        short => "Фионова Л.Р.",
        role  => "Декан ФВТ",
        email => 'fvt@pnzgu.ru',
        phone => "+7 (8412) 66-65-60",
      },
      {
        person_id => 2,
        name  => "Бычков Андрей Станиславович",
        short => "Бычков А.С.",
        role  => "Заместитель декана по учебной работе",
        email => 'fvt@pnzgu.ru',
        phone => "+7 (8412) 66-65-60",
      },
      {
        person_id => 3,
        name  => "Писарев Аркадий Петрович",
        short => "Писарев А.П.",
        role  => "Заместитель декана по учебной работе",
        email => 'pisarev60@mail.ru',
        phone => "+7 (8412) 66-65-60",
      },
      {
        person_id => 4,
        name  => "Мойко Наталья Валентиновна",
        short => "Мойко Н.В.",
        role  => "Заместитель декана по учебной работе",
        email => 'fvt@pnzgu.ru',
        phone => "+7 (8412) 66-65-60",
      },
      {
        person_id => 5,
        name  => "Катышева Марина Александровна",
        short => "Катышева М.А.",
        role  => "Заместитель декана по молодежной политике и воспитательной деятельности",
        email => 'fvt@pnzgu.ru',
        phone => "+7 (8412) 66-65-60",
      },
    );

    my $ins_people = $dbh->prepare(q{
        INSERT INTO people (person_id, name, short, role, email, phone)
        VALUES (?, ?, ?, ?, ?, ?)
    });

    for my $p (@people) {
        $ins_people->execute(
            $p->{person_id}, $p->{name}, $p->{short}, $p->{role}, $p->{email}, $p->{phone}
        );
    }

    my $ins_hours = $dbh->prepare(q{
        INSERT INTO reception_hours (person_id, weekday, time, note)
        VALUES (?, ?, ?, ?)
    });

    # Фионова Л.Р.
    $ins_hours->execute(1, 1, "12:00-13:30", "");
    $ins_hours->execute(1, 2, "13:15-13:45", "");
    $ins_hours->execute(1, 4, "13:15-13:45", "");

    # Мойко Н.В.
    $ins_hours->execute(4, 1, "09:00-13:15", "");
    $ins_hours->execute(4, 2, "09:00-14:00", "");
    $ins_hours->execute(4, 3, "11:40-14:00", "I неделя");
    $ins_hours->execute(4, 4, "11:00-14:00", "II неделя");

    # Бычков А.С.
    $ins_hours->execute(2, 1, "09:00-11:25", "I неделя");
    $ins_hours->execute(2, 2, "13:15-15:00", "I неделя");
    $ins_hours->execute(2, 3, "11:40-15:35", "по перерывам");
    $ins_hours->execute(2, 4, "13:15-15:00", "I неделя");
    $ins_hours->execute(2, 1, "09:00-11:40; 13:15-15:00", "II неделя");

    # Писарев А.П.
    $ins_hours->execute(3, 1, "09:00-11:40", "I неделя; по перерывам");
    $ins_hours->execute(3, 2, "09:00-11:30", "I неделя");
    $ins_hours->execute(3, 3, "09:00-13:15", "I неделя; по перерывам");
    $ins_hours->execute(3, 4, "09:00-11:40", "II неделя");
    $ins_hours->execute(3, 5, "13:15-15:00", "II неделя");

    # Катышева М.А.
    $ins_hours->execute(5, 1, "11:00-12:00", "");
});

print "Reception initialized in SQLite: $db_path\n";
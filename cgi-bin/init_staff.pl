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

my $faculty_id = Db::id_for_unique_name($dbh, "faculties", "faculty_id", "short_name", "ФВТ");

# Административный персонал
my @people = (
    { name => "Фионова Людмила Римовна", short => "Фионова Л.Р.", role => "Декан ФВТ", email => 'fvt@pnzgu.ru', phone => "+7 (8412) 66-65-60" },
    { name => "Бычков Андрей Станиславович", short => "Бычков А.С.", role => "Заместитель декана по учебной работе", email => 'fvt@pnzgu.ru', phone => "+7 (8412) 66-65-60" },
    { name => "Писарев Аркадий Петрович", short => "Писарев А.П.", role => "Заместитель декана по учебной работе", email => 'pisarev60@mail.ru', phone => "+7 (8412) 66-65-60" },
    { name => "Мойко Наталья Валентиновна", short => "Мойко Н.В.", role => "Заместитель декана по учебной работе", email => 'fvt@pnzgu.ru', phone => "+7 (8412) 66-65-60" },
    { name => "Катышева Марина Александровна", short => "Катышева М.А.", role => "Заместитель декана по молодежной политике и воспитательной деятельности", email => 'fvt@pnzgu.ru', phone => "+7 (8412) 66-65-60" },
);

# Преподаватели
my @teachers = (
    "Иванов И.И.", "Петров П.П.", "Сидорова А.А.", "Кузнецов М.М.",
    "Орлов Д.Д.", "Зайцева Н.Н.", "Романенко В.В.", "Смирнов А.А.",
    "Тында А.Н.", "Соколова Т.Т.", "Егоров Н.Н.", "Громова В.В.",
    "Борисов С.С.", "Мельников А.А.", "Лебедева И.И.", "Макаров К.К."
);

Db::txn($dbh, sub {
    $dbh->do("DELETE FROM staff");

    my $ins_staff = $dbh->prepare(q{
        INSERT INTO staff (faculty_id, name, short_name, position, email, phone, is_teacher)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    });

    # Вставка административного персонала
    for my $p (@people) {
        $ins_staff->execute(
            $faculty_id,
            $p->{name},
            $p->{short},
            $p->{role},
            $p->{email},
            $p->{phone},
            0   
        );
    }

    # Вставка преподавателей
    my %seen;
    for my $t (@teachers) {
        next if $seen{$t}++;
        $ins_staff->execute(
            $faculty_id,
            $t,
            $t,                 
            'Преподаватель',
            undef,
            undef,
            1                  
        );
    }
});

print "Staff initialized in SQLite: $db_path\n";
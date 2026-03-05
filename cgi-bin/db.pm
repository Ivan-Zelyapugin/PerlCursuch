package Db;

use strict;
use warnings;
use utf8;

use DBI;
use Encode qw(decode);

# Открыть соединение с SQLite
sub connect_sqlite {
    my (%opt) = @_;
    my $db_path = $opt{db_path} // die "connect_sqlite: db_path is required";

    my $dbh = DBI->connect(
        "dbi:SQLite:dbname=$db_path",
        "",
        "",
        {
            RaiseError     => 1,
            PrintError     => 0,
            AutoCommit     => 1,
            sqlite_unicode => 1,  
        }
    ) or die "DBI connect failed: $DBI::errstr";

    $dbh->do("PRAGMA foreign_keys = ON");

    return $dbh;
}

# Выполнить SQL файл 
sub exec_sql_file {
    my ($dbh, $file_path) = @_;
    open my $fh, "<:raw", $file_path or die "Cannot open $file_path: $!";
    local $/;
    my $sql = <$fh>;
    close $fh;

    $sql = decode("UTF-8", $sql);

    for my $stmt (split /;\s*(?:\r?\n)+/s, $sql) {
        $stmt =~ s/^\s+|\s+$//g;
        next if $stmt eq '';
        $dbh->do($stmt);
    }
}

sub id_for_unique_name {
    my ($dbh, $table, $id_col, $name_col, $name) = @_;
    die "id_for_unique_name: name is required" if !defined $name || $name eq '';

    my ($id) = $dbh->selectrow_array(
        "SELECT $id_col FROM $table WHERE $name_col = ?",
        undef,
        $name
    );
    return $id if defined $id;

    $dbh->do("INSERT INTO $table ($name_col) VALUES (?)", undef, $name);
    return $dbh->sqlite_last_insert_rowid();
}

# Обёртка под транзакцию
sub txn {
    my ($dbh, $code) = @_;
    $dbh->begin_work;
    eval {
        $code->();
        1;
    } or do {
        my $err = $@ || "unknown error";
        eval { $dbh->rollback; };
        die $err;
    };
    $dbh->commit;
}

1;
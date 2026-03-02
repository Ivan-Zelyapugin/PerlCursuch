package Db;

use Encode qw(encode decode);

use strict;
use warnings;
use utf8;

use Fcntl qw(O_CREAT O_RDWR);
use DB_File;

sub _open_hash {
    my ($path) = @_;
    my %h;
    tie %h, 'DB_File', $path, O_CREAT|O_RDWR, 0644, $DB_HASH
      or die "DB_File tie failed for $path: $!";
    return \%h;
}

sub put_row {
    my ($path, $id, $row) = @_;
    my $h = _open_hash($path);
    $h->{$id} = encode("UTF-8", _encode($row));
    untie %$h;
}

sub get_all {
    my ($path) = @_;
    my $h = _open_hash($path);
    my @rows = map { _decode(decode("UTF-8", $h->{$_})) } sort { $a <=> $b } keys %$h;
    untie %$h;
    return \@rows;
}

sub find_by {
    my ($path, $field, $value) = @_;
    my $h = _open_hash($path);
    my @rows;
    for my $k (keys %$h) {
        my $r = _decode(decode("UTF-8", $h->{$k}));
        push @rows, $r if defined $r->{$field} && $r->{$field} eq $value;
    }
    untie %$h;
    return \@rows;
}

# key=value;key=value, с экранированием ; и =
sub _encode {
    my ($r) = @_;
    my @pairs;
    for my $k (sort keys %$r) {
        my $v = defined($r->{$k}) ? $r->{$k} : "";
        $v =~ s/;/\\;/g;
        $v =~ s/=/\\=/g;
        push @pairs, "$k=$v";
    }
    return join(";", @pairs);
}

sub _decode {
    my ($s) = @_;
    my %r;
    for my $p (split /(?<!\\);/, $s) {
        my ($k, $v) = split /(?<!\\)=/, $p, 2;
        $k =~ s/\\([;=])/$1/g if defined $k;
        $v =~ s/\\([;=])/$1/g if defined $v;
        $r{$k} = $v;
    }
    return \%r;
}

1;
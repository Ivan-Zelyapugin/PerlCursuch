package Html;

use strict;
use warnings;
use utf8;

use CGI qw(escapeHTML);

sub page_begin {
    my (%p) = @_;
    my $title = $p{title} // "Сайт факультета";

    return
      "Content-Type: text/html; charset=UTF-8\r\n\r\n" .
      "<!doctype html><html lang='ru'><head><meta charset='utf-8'>" .
      "<title>" . escapeHTML($title) . "</title>" .
      "<link rel='stylesheet' href='/style.css'>" .
      "<script>
        function jsBtn(){ alert('Кнопка с JS нажата. Поздравляю, ты активировал диалоговое окно.'); }
      </script>" .
      "</head><body>" .
      "<header>" .
      "<nav>" .
      "<a href='/index.html'>Главная</a>" .
      "<a href='/history.html'>История</a>" .
      "<a href='/departments.html'>Кафедры</a>" .
      "<a href='/schedule.html'>Расписание</a>" .
      "<a href='/reception.html'>Часы приёма</a>" .
      "</nav>" .
      "</header>" .
      "<main><a id='top'></a>";
}

sub page_end {
    return
      "<p class='small'><a href='#top'>Наверх</a> | <a href='#bottom'>В конец</a></p>" .
      "<a id='bottom'></a></main>" .
      "<footer class='small'>VAR22, Perl CGI, DB_File. Живём.</footer>" .
      "</body></html>";
}

sub img_button {
    my (%p) = @_;
    my $href = $p{href} // "/index.html";
    my $src  = $p{src}  // "/img/logo.png";
    my $alt  = $p{alt}  // "Кнопка-картинка";
    return "<a href='" . escapeHTML($href) . "'><img src='" . escapeHTML($src) .
           "' alt='" . escapeHTML($alt) . "' width='64' height='64'></a>";
}

1;
%This class provides the styling and formatting for the bylaws of the VSETH.
%It contains the two following options:
% - bylaw: styling for the full bylaws (Rechtssammlung)
% - regulation: styling for a single regulations (Reglement/Verordnung)

%-------------------
%Class setup
%-------------------
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{vseth-bylaws}[2024/01/01 VSETH Bylaws]

%Minimal requierements for a class file, will be overwritten by the scrreprt class and geometry.
\renewcommand{\normalsize}{\fontsize{10pt}{12pt}\selectfont} 
\setlength{\textwidth}{6.5in} 
\setlength{\textheight}{8in} 

%Load the scrreprt class which will act as a base for the bylaws
\LoadClass[DIV=14, chapterentrydots, parskip]{scrreprt}


%-------------------
%List of packages used
%-------------------
\RequirePackage[utf8]{inputenc}
\RequirePackage[OT1]{fontenc}
\RequirePackage{microtype}
\RequirePackage[all]{nowidow}
\RequirePackage[nswissgerman]{babel}
\RequirePackage{geometry}
\RequirePackage{enumitem}
\RequirePackage{graphicx}
\RequirePackage{svg}
\RequirePackage{array}
\RequirePackage{booktabs}
\RequirePackage{longtable}
\RequirePackage{setspace}
\RequirePackage{float}
\RequirePackage{lastpage}
\RequirePackage{scrlayer-scrpage}
\RequirePackage[default,regular,bold]{sourcesanspro}
\RequirePackage{xcolor}
%Should be the last package loaded
\RequirePackage{hyperref}

% More error context
\errorcontextlines=10

%--------------------------------
%Style setup
%--------------------------------

%Defines the VSETH CI Colors
\definecolor{vsethcyan}{cmyk}{100,0,0,0}
\definecolor{salsared}{cmyk}{0,89,66,0}

%Setup the formatting of the links
\hypersetup{
  % colors
  colorlinks={true},
  linkcolor={vsethcyan},
  urlcolor={vsethcyan},
  % bookmarks in PDF
  bookmarksnumbered={true},
  % Only numbers in TOC should be links, as all the cyan in kinda ugly.
  linktoc={page}
} 

%Setup for the date
\newcommand{\@documentdate}{Change with \texttt{\textbackslash setdate\{date\}}}
\newcommand{\setdate}[1]{
    \renewcommand{\@documentdate}{#1}
}

%Activate the headers if the option is set
\DeclareOption{headers}{
  \ohead[
          \begin{tabular}{>{\raggedright}p{1.1cm}p{2.5cm}}
              {\fontseries{m}\selectfont \textcolor{vsethcyan}{D}} & \@documentdate \\ & \\
          \end{tabular}
  ]{}
}{}

\ProcessOptions\relax

%Fonts and formatting of the headers
\setcounter{secnumdepth}{0}
%\renewcommand*{\thesection}{\arabic{section}}
\RedeclareSectionCommand[afterskip=0pt, runin=false, tocindent=1em, tocnumwidth=1.25em]{section}
\RedeclareSectionCommand[afterskip=0pt, runin=false, tocindent=3.25em, tocnumwidth=2em]{subsection}
\RedeclareSectionCommand[afterskip=0pt, runin=false]{subsubsection}
\setkomafont{title}{\fontseries{b}\fontsize{26}{32}\selectfont}
\setkomafont{subtitle}{\fontseries{m}\fontsize{15}{19}\selectfont \color{gray}}
\setkomafont{chapter}{\fontseries{b}\fontsize{26}{32}\selectfont}
\setkomafont{subtitle}{\fontseries{m}\fontsize{15}{19}\selectfont \color{gray}}
\setkomafont{section}{\fontseries{b}\fontsize{20}{25}\selectfont}
\setkomafont{subsection}{\fontseries{b}\fontsize{16}{20}\selectfont \color{vsethcyan}}
\setkomafont{subsubsection}{\fontseries{b}\fontsize{14}{17}\selectfont}

% Page setup
\geometry{
    paper=a4paper,
    includeheadfoot,
    top=2cm,
    bottom=2cm,
    left=3cm,
    right=3cm,
    head=41pt,
    headsep=1cm,
    foot=41pt,
    footskip=1cm,
    verbose=true,
}

% Header/footer
\setkomafont{pageheadfoot}{\sffamily}
\cfoot*{
    \textbf{- \thepage\ / \pageref*{LastPage} -} \\
    \noindent\textcolor{vsethcyan}{\rule\textwidth{1mm}} \\
}

%VSETH Logo upper left corner of every page
%TODO: Make the path to the logo configurable
\ihead*{
  \includesvg[width=57mm]{assets/vseth_Logo_bylines_Verband.svg}
}

%TODO: Make this a toggle

%-------------------
%Title Page setup
%#1: Title
%#2: Date
%-------------------
\newcommand{\maketitlepage}[2]{
  \begin{titlepage}
  \centering
  \hspace{0pt}
  \vfill
  \includesvg[width=80mm]{assets/vseth_Logo_bylines_Verband.svg}
  \par
  {\usekomafont{title} \textbf{#1} \par }
  {\usekomafont{subtitle} #2 \par }
  \vfill
  \end{titlepage}
}

% Behavior of \maketitle
\makeatletter
\renewcommand{\maketitle}{\bgroup\setlength{\parindent}{0pt}
    \vspace*{0.5cm} % for some reasor the effective space is twice as large
    \begin{flushleft}
        {\usekomafont{title} \@title}\par\vspace*{14pt}{\usekomafont{subtitle} \@subtitle}
    \end{flushleft}\egroup\thispagestyle{plain.scrheadings}\vspace*{4pt}
}
\makeatother

%---------------------
%Enviroment setup
%---------------------

% Define a counter representation (like arabic) for latin numerals (from chapter 8 of the enumitem manual)
% The numerals are arbitrarily limited to 12 as everything above is both too wide and too unreasonable for
% mhaessig's taste.
\makeatletter
\def\latin#1{\expandafter\@latin\csname c@#1\endcsname}
\def\@latin#1{\ifcase#1\or
			bis
		\or
			ter
		\or
			quater
		\or
			quinquies
		\or
			sexies
		\or
			septies
		\or
			octies
		\or
			novies
		\or
			decies
		\or
			undecies
		\or
			duodecies\fi}
\makeatother
\AddEnumerateCounter{\latin}{\@latin}{duodecies}


\newenvironment{article}[2]{\textbf{Art.\ #1\ #2}}{\par}

% Paragraphs are aligned all the way on the left page margin and text flows around the labels.
\newlist{paragraphs}{enumerate}{1}
\setlist[paragraphs]{
  label        = {\textsuperscript{\arabic*}},
  ref          = {Abs.\ \arabic*},
  align        = left,
  leftmargin   = 0em,   % Make sure text flows all the way to the left page margin.
  labelindent  = 0em,   % Make sure the labels are all the way on the left page margin.
  labelsep     = 0.5ex, % Label separation of about a space.
  labelwidth   = 1ex,   % For some reason this needs to be fixed for this to work. Makes no sense, but it works.
  itemindent   = !,     % Calculate the indent of the first line of text based on the values above.
  before*      = \nopagebreak,
  first*       = \nopagebreak,
  beginpenalty = 100000,
  midpenalty   = 1000,
  noitemsep,
  nosep,
  % Uncomment line below to bebug horizontal spacing.
  %first*       = \DrawEnumitemLabel,
}

% Paragraphs are aligned all the way on the left page margin and text flows around the labels.
\newlist{insertedparagraphs}{enumerate}{1}
\setlist[insertedparagraphs]{
  label        = {\textsuperscript{\arabic{paragraphsi}\latin*}},
  ref          = {Abs.\ \arabic{enumi}\textsuperscript{\latin*}},
  align        = left,
  leftmargin   = 0em,   % Make sure text flows all the way to the left page margin.
  labelindent  = 0em,   % Make sure the labels are all the way on the left page margin.
  labelsep     = 0.5ex, % Label separation of about a space.
  labelwidth   = 1ex,   % For some reason this needs to be fixed for this to work. Makes no sense, but it works.
  itemindent   = !,     % Calculate the indent of the first line of text based on the values above.
  before*      = \nopagebreak,
  first*       = \nopagebreak,
  beginpenalty = 100000,
  midpenalty   = 1000,
  noitemsep,
  nosep,
  % Uncomment line below to bebug horizontal spacing.
  %first*       = \DrawEnumitemLabel,
}

% The list definitions below need a solid understanding of the chapter on horizontal spacing
% in the enumitem manual (https://mirror.foobar.to/CTAN/macros/latex/contrib/enumitem/enumitem.pdf).

\newlist{letters}{enumerate}{1}
\setlist[letters]{
  label        = {\alph*.},
  ref          = {lit.\ \alph*},
  labelindent  = 3em, % How much to indent the list.
  labelwidth   = 2em, % Needs to be a known value to calculate the labelindent for the inserted list.
  labelsep     = 1em, % Needs to be a known value to calculate the labelindent for the inserted list.
  itemindent   = 0em, % The labels are never wider than the labelwidth we fixed above, therefore we can fix this.
  leftmargin   = !,   % Calculate margin to fit the fixed values.
  align        = left,
  beginpenalty = 100000,
  midpenalty   = 1000,
  noitemsep,
  % Uncomment line below to bebug horizontal spacing.
  %first*       = \DrawEnumitemLabel,
}

% This list needs to be aligned to match the indentation of letters.
\newlist{insertedletters}{enumerate}{1}
\setlist[insertedletters]{
  label        = {\alph{lettersi}.\textsuperscript{\hspace{-2pt}\latin*}\hspace{2pt}}, %The hspace ensures that the dot is not too far away from the letter.
  ref          = {lit.\ \alph{lettersi}\textsuperscript{\latin*}},
  labelindent  = -3em, % Place label at the same place (labelwidth + labelsep of letters)
  labelsep     = 1em,  % Ensure the separation from the label.
  leftmargin   = 0em,  % Ensure that the text starts at the same place as letters.
  labelwidth   = *,    % Ensure that the label can overflow if the latin numeral is large.
  itemindent   = !,    % Calculate to fit the fixed values.
  align        = left,
  beginpenalty = 100000,
  midpenalty   = 1000,
  noitemsep,
  % Uncomment line below to bebug horizontal spacing.
  %first*       = \DrawEnumitemLabel,
}

\newlist{numerals}{enumerate}{1}
\setlist[numerals]{
  label        = {\arabic*.},
  ref          = {\arabic*},
  align        = left,
  labelindent  = 0em, % Do not indent any more.
  labelwidth   = 2em, % Needs to be a known value to calculate the labelindent for the inserted list.
  labelsep     = 1em, % Needs to be a known value to calculate the labelindent for the inserted list.
  itemindent   = 0em, % The labels are never wider than the labelwidth we fixed above, therefore we can fix this.
  leftmargin   = !,   % Calculate margin to fit the fixed values.
  beginpenalty = 100000,
  midpenalty   = 1000,
  noitemsep,
  % Uncomment line below to bebug horizontal spacing.
  %first*       = \DrawEnumitemLabel,
}

% This list needs to be aligned to match the indentation of numerals.
\newlist{insertednumerals}{enumerate}{1}
\setlist[insertednumerals]{
  label        = {\arabic{numeralsi}.\textsuperscript{\hspace{-2pt}\latin*}\hspace{3.5pt}}, %The hspace ensures that the dot is not too far away from the numeral.
  ref          = {Ziff. \arabic{numeralsi}\textsuperscript{\latin*}},
  align        = left,
  labelindent  = -3em, % Place label at the same place.
  labelsep     = 1em,  % Ensure separation between label and content.
  leftmargin   = 0em,  % Ensure that the text starts at the same place as numerals.
  labelwidth   = *,    % Ensure that the label can overflow if the latin numeral is large.
  itemindent   = !,    % Calculate to fit the fixed values.
  beginpenalty = 100000,
  midpenalty   = 1000,
  noitemsep,
  % Uncomment line below to bebug horizontal spacing.
  %first*       = \DrawEnumitemLabel,
}

\endinput

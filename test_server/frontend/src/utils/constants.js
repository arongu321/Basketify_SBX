export const ACCESS_TOKEN = 'access';
export const REFRESH_TOKEN = 'refresh';

// Filter constants for Stats Page
// FR25 - Constants for filter options in the frontend
// FR25 - NBA seasons available for filtering
export const NBA_SEASONS = {
    team: [
        '2009-10',
        '2010-11',
        '2011-12',
        '2012-13',
        '2013-14',
        '2014-15',
        '2015-16',
        '2016-17',
        '2017-18',
        '2018-19',
        '2019-20',
        '2020-21',
        '2021-22',
        '2022-23',
        '2023-24',
        '2024-25',
    ],
    player: ['2022-23', '2023-24', '2024-25'],
};

// FR25 - Season types for filtering
export const SEASON_TYPES = [
    'Preseason',
    'Regular Season',
    'Postseason',
    'NBA Cup Finals',
    'Play-In Tournament',
];

// FR25 - NBA divisions for filtering
export const NBA_DIVISIONS = [
    'Atlantic',
    'Central',
    'Southeast',
    'Northwest',
    'Pacific',
    'Southwest',
];

// FR25 - NBA conferences for filtering
export const NBA_CONFERENCES = ['East', 'West'];

// FR25 - Game types for filtering
export const GAME_TYPES = ['All', 'Interconference', 'Intraconference'];

// FR25 - Game outcomes for filtering
export const GAME_OUTCOMES = ['All', 'Win', 'Loss'];

// FR25 - Months for filtering by month
export const MONTHS = [
    { value: '1', label: 'January' },
    { value: '2', label: 'February' },
    { value: '3', label: 'March' },
    { value: '4', label: 'April' },
    { value: '5', label: 'May' },
    { value: '6', label: 'June' },
    { value: '7', label: 'July' },
    { value: '8', label: 'August' },
    { value: '9', label: 'September' },
    { value: '10', label: 'October' },
    { value: '11', label: 'November' },
    { value: '12', label: 'December' },
];

// FR25 - NBA teams for filtering by opponent
export const NBA_TEAMS = [
    'Atlanta Hawks',
    'Boston Celtics',
    'Brooklyn Nets',
    'Charlotte Hornets',
    'Chicago Bulls',
    'Cleveland Cavaliers',
    'Dallas Mavericks',
    'Denver Nuggets',
    'Detroit Pistons',
    'Golden State Warriors',
    'Houston Rockets',
    'Indiana Pacers',
    'Los Angeles Clippers',
    'Los Angeles Lakers',
    'Memphis Grizzlies',
    'Miami Heat',
    'Milwaukee Bucks',
    'Minnesota Timberwolves',
    'New Orleans Pelicans',
    'New York Knicks',
    'Oklahoma City Thunder',
    'Orlando Magic',
    'Philadelphia 76ers',
    'Phoenix Suns',
    'Portland Trail Blazers',
    'Sacramento Kings',
    'San Antonio Spurs',
    'Toronto Raptors',
    'Utah Jazz',
    'Washington Wizards',
];

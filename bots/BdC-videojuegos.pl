% -*- prolog -*-
% ==============================================================================
% BASE DE CONOCIMIENTOS: JUEGOS EN METACRITIC
% ==============================================================================
% NOTA: los puntajes son de metacritic.com Cuando un juego no tiene metascore (early access, sin
% reseñas suficientes) se usa el átomo 'na'.

% ==============================================================================
% DEVELOPERS
% developer(nombre_developer)
% ==============================================================================
developer(nintendo).
developer(rockstar_north).
developer(rockstar_games).
developer(valve).
developer(cd_projekt_red).
developer(fromsoftware).
developer(larian_studios).
developer(supergiant_games).
developer(neversoft).
developer(riot_games).
developer(pocketpair).
developer(studio_wildcard).
developer(blizzard_entertainment).
developer(the_game_kitchen).
developer(team_salvato).
developer(team_cherry).
developer(studio_mdhr).
developer(yacht_club_games).
developer(motion_twin).
developer(omocat).
developer(nomada_studio).
developer(kojima_productions).
developer(localthunk).
developer(atlus).

% ==============================================================================
% JUEGOS
% juegos(titulo, año, plataformas, genero, metascore, user_score, developer)
%   - plataformas: lista de plataformas
%   - metascore: 0-100 (críticos) o 'na' si no tiene
%   - user_score: 0-10 (usuarios) o 'na' si no tiene
% ==============================================================================

% --- ACCIÓN / AVENTURA ---
juegos(the_legend_of_zelda_ocarina_of_time, 1998, [n64], accion_aventura, 99, 9.1, nintendo).
juegos(grand_theft_auto_iv, 2008, [ps3, xbox360, pc], accion_aventura, 98, 8.4, rockstar_north).
juegos(red_dead_redemption_2, 2018, [ps4, xbox_one, pc], accion_aventura, 97, 9.0, rockstar_games).
juegos(death_stranding_directors_cut, 2021, [ps5, pc, xbox_series_x], accion_aventura, 85, 8.2, kojima_productions).

% --- RPG/JRPG ---
juegos(the_witcher_3_wild_hunt_remastered, 2026, [pc, ps5, xbox_series_x, switch_2], rpg, 94, 8.4, cd_projekt_red).
juegos(elden_ring, 2022, [pc, ps4, ps5, xbox_one, xbox_series_x], rpg, 96, 8.4, fromsoftware).
juegos(baldurs_gate_3, 2023, [pc, ps5, xbox_series_x], rpg, 96, 9.1, larian_studios).
juegos(omori, 2020, [pc, switch, ps4, xbox_one, xbox_series_x], rpg, 88, 9.0, omocat).
juegos(metaphor_refantazio, 2024, [pc, ps4, ps5, xbox_series_x, switch], jrpg, 94, 8.5, atlus).

% --- MMORPG / MOBA ---
juegos(world_of_warcraft, 2004, [pc], mmorpg, 93, 7.5, blizzard_entertainment).
juegos(league_of_legends, 2009, [pc], moba, 78, 4.7, riot_games).
juegos(deadlock, 2026, [pc], moba, na, na, valve).

% --- PLATAFORMAS ---
juegos(super_mario_galaxy, 2007, [wii, switch], plataformas, 97, 9.0, nintendo).
juegos(shovel_knight, 2014, [pc, wii_u, n3ds, ps4, ps3, xbox_one, ps_vita], plataformas, 85, 8.1, yacht_club_games).
juegos(gris, 2018, [pc, switch, ps4, xbox_one, ps5, xbox_series_x], plataformas, 83, 9.0, nomada_studio).
juegos(cuphead, 2017, [pc, xbox_one, switch, ps4], plataformas, 86, 8.5, studio_mdhr).

% --- METROIDVANIA / ROGUELIKE ---
juegos(hollow_knight, 2017, [pc, wii_u, switch, ps4, xbox_one, ps5, switch_2], metroidvania, 90, 9.0, team_cherry).
juegos(blasphemous, 2019, [pc, switch, ps4, xbox_one], metroidvania, 77, 7.9, the_game_kitchen).
juegos(dead_cells, 2018, [pc, switch, ps4, xbox_one], metroidvania, 89, 8.3, motion_twin).
juegos(hades, 2020, [pc, switch, ps4, ps5, xbox_one, xbox_series_x], roguelike, 93, 8.5, supergiant_games).
juegos(balatro, 2024, [pc, switch, ps4, ps5, xbox_one, xbox_series_x, switch_2], roguelike, 90, 8.4, localthunk).


% --- SHOOTER / PUZZLE ---
juegos(half_life, 1998, [pc, ps2], shooter, 96, 8.9, valve).
juegos(half_life_2, 2004, [pc, xbox], shooter, 96, 9.1, valve).
juegos(portal, 2007, [pc], puzzle, 90, 8.8, valve).
juegos(portal_2, 2011, [pc, ps3, xbox360], puzzle, 95, 8.9, valve).
juegos(left_4_dead_2, 2009, [pc, xbox360], shooter, 89, 8.2, valve).
juegos(counter_strike_2, 2023, [pc], shooter, 82, 5.5, valve).

% --- SUPERVIVENCIA ---
juegos(palworld, 2026, [pc, xbox_series_x, xbox_one, ps5], supervivencia, 79, 7.5, pocketpair).
juegos(ark_survival_evolved, 2017, [pc, ps4, xbox_one, switch], supervivencia, 70, 6.5, studio_wildcard).

% --- NOVELA VISUAL ---
juegos(doki_doki_literature_club, 2017, [pc, switch, ps4, xbox_one], novela_visual, 78, 8.3, team_salvato).

% --- DEPORTES ---
juegos(tony_hawks_pro_skater_2, 2000, [ps1, n64, pc, game_boy_advance], deportes, 91, 8.2, neversoft).

% ==============================================================================
% REGLAS DE EJEMPLO (consultas útiles)
% ==============================================================================

% Juegos de un developer
juegos_de(Dev, Titulo) :-
    juegos(Titulo, _, _, _, _, _, Dev).

% Juegos de un género
juegos_genero(Genero, Titulo) :-
    juegos(Titulo, _, _, Genero, _, _, _).

% Juegos disponibles en una plataforma
juegos_plataforma(Plataforma, Titulo) :-
    juegos(Titulo, _, Plataformas, _, _, _, _),
    member(Plataforma, Plataformas).

% Juegos con metascore mayor o igual a un minimo (ignora los 'na')
juegos_con_metascore_minimo(Min, Titulo, Metascore) :-
    juegos(Titulo, _, _, _, Metascore, _, _),
    number(Metascore),
    Metascore >= Min.

% Juegos lanzados en un rango de años
juegos_entre(Desde, Hasta, Titulo) :-
    juegos(Titulo, Anio, _, _, _, _, _),
    Anio >= Desde,
    Anio =< Hasta.

% Developer con juegos sobre cierto metascore: devuelve el juego, su metascore y el developer
developer_destacado(Dev, Min, Titulo, Meta) :-
    developer(Dev),
    juegos(Titulo, _, _, _, Meta, _, Dev),
    number(Meta),
    Meta >= Min.

% ==============================================================================
% CONSULTAS DE PRUEBA
% ==============================================================================
% ?- juegos_de(valve, T).
% ?- juegos_genero(metroidvania, T).
% ?- juegos_plataforma(switch, T).
% ?- juegos_con_metascore_minimo(90, T, M).
% ?- juegos_entre(2017, 2020, T).
% ?- developer_destacado(valve, 90, T, M).
% ?- developer_destacado(Dev, 97, T, M).
:- module('spec', [trace_expression/2, match/2]).
:- use_module(monitor('deep_subdict')).
match(_event, a) :- deep_subdict(_{'event':"a"}, _event).
match(_event, h) :- deep_subdict(_{'event':"h"}, _event).
match(_event, j) :- deep_subdict(_{'event':"j"}, _event).
match(_event, k) :- deep_subdict(_{'event':"k"}, _event).
match(_event, o) :- deep_subdict(_{'event':"o"}, _event).
match(_event, n) :- deep_subdict(_{'event':"n"}, _event).
match(_event, r) :- deep_subdict(_{'event':"r"}, _event).
match(_event, x) :- deep_subdict(_{'event':"x"}, _event).
match(_, any).
trace_expression('Main', Main) :- Main=(((((((((h:eps)*(state11:eps))\/((j:eps)*(state11:eps)))\/((k:eps)*(state11:eps)))\/((o:eps)*(state11:eps)))\/((n:eps)*(state11:eps)))\/((r:eps)*(state11:eps)))\/((x:eps)*(state11:eps)))\/((a:eps)*(state13:eps))).

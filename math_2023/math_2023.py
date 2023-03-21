import os
import logging
from multiprocessing import Pool

op = ['+', '-', '*', '/']


def all_values(v):
  if len(v) == 1:
    yield v
    return

  for x in range(len(v)):
    vv = v[:]
    del vv[x]

    for vvv in all_values(vv):
      result = [v[x]]
      result.extend(vvv)
      yield result


def calc(v):
  if len(v) == 1:
    yield f'{v[0]}'
    return

  for desc in calc(v[1:]):
    for x in op:
      yield f'{v[0]}{x}{desc}'


def find_2023(v):
  with open(f'find_2023_{os.getpid()}', 'a') as f:
    for desc in calc(v):
      try:
        if eval(desc) == 2023:
          f.write(desc + '\n')
      except:
        logging.exception('error')


def math_2023():
  value = [x for x in range(1, 11)]

  print(value, op)

  with Pool(10) as p:
    p.map(find_2023, all_values(value))


if __name__ == '__main__':
  math_2023()

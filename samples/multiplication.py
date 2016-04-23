#!/usr/bin/env python3

def get_questions(): 
    result = []
    for a in range(13):
        for b in range(13):
            result.append(
              {
                'q': [ str(a) + ' × ' + str(b)]
              , 'a': [ str(a * b) ]
              }
            )
    return result


if __name__ == "__main__":
    print("\n".join(map(str, (get_questions()))))

def SIR(N0, I0, a, b, days, R0=0, samples=200, steps=10000):
    L, S, I, R = [], N0-R0-I0, I0, R0
    step, sampleStep = days/steps, steps //samples
    for i in range(steps+1):
        if i%sampleStep == 0:
            d = i*step
            L.append((d,S,I,R))
        S, I = S*(1-a*I*step), I*(1+(a*S-b)*step)
        R = N0-S-I
    return [list(map(lambda p: (p[0],p[k]),L)) for k in [1,2,3]]
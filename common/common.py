import pandas as pd
import numpy as np
import os, sys, glob
import platform
import time
import matplotlib.pyplot as plt
import yaml
import datetime
from matplotlib.font_manager import FontProperties
from matplotlib.cm import get_cmap
import pickle

# framerate = 50.0

EPS = 1e-15
theta=0.005

class Point:
    def __init__(self, x, y):
        self.r = x
        self.i = y

    def conj(self):
        self.i *= (-1)

    def real(self):
        return self.r

    def imag(self):
        return self.i

    def equal(self, a):
        return (self.r == a.r) and (self.i == a.i)


class Line:
    def __init__(self, a, b):
        self.x = b.r - a.r
        self.y = b.i - a.i
        self.points = [a, b]

    def values(self):
        return np.array([self.x, self.y])


class Polygon:
    def __init__(self):
        self.vertices = []
        self.is_polygon= True
        self.is_space=False
        self.is_interval=False
    def isempty(self):
        if (self.is_polygon) and (len(self.vertices)):
            return False
        elif (self.is_space) or (self.is_interval):
            return False
        else:
            return True
    def space(self,l,u):
        self.lower=l
        self.upper=u
        self.is_polygon=False
        self.is_space=True

    def interval(self,l,u):
        self.l=l
        self.u=u
        self.is_polygon = False
        self.is_interval=True

    def add_vertex(self, a):
        if a not in self.vertices:
            self.vertices.append(a)

    def del_vertex(self, a):
        for p in self.vertices:
            if p.equal(a):
                self.vertices.remove(p)

    def is_vertex(self, a):
        for p in self.vertices:
            if p.equal(a):
                return True
        return False


def intersect(a, b, c, d):
    d1 = np.cross(Line(a, c).values(), Line(a, b).values())
    d2 = np.cross(Line(a, d).values(), Line(a, b).values())
    if abs(d1 - d2) > EPS: # chech if parallel or identical
        inter = Point((d1 * d.r - d2 * c.r) / (d1 - d2), (d1 * d.i - d2 * c.i) / (d1 - d2))
        return True, inter
    return False, None


def polygon_cut(g, line, lower):
    g_new = Polygon()
    for i in range(len(g.vertices)):
        j = (i + 1) % len(g.vertices)
        in1 = np.cross(line.values(), Line(line.points[0], g.vertices[i]).values()) > EPS
        in2 = np.cross(line.values(), Line(line.points[0], g.vertices[j]).values()) > EPS

        if (lower and not in1):
            g_new.add_vertex(g.vertices[i])
        if (not lower and in1):
            g_new.add_vertex(g.vertices[i])
        if (in1 ^ in2):
            bool,inter = intersect(line.points[0], line.points[1], g.vertices[i], g.vertices[j])
            if bool and (not g_new.is_vertex(inter)):
                g_new.add_vertex(inter)
    return g_new



def FCSA(fj, fcs, p_start, p_next):
    if fj == 'quadratic':
        #construct two starts l and u
        p0=P[p_start]
        p1=P[p_next]
        u=Line(Point(0,(p1-p0+theta)/float(p_next-p_start)),Point((p1-p0+theta)/float(p_next**2-p_start**2),0))
        l=Line(Point(0,(p1-p0-theta)/float(p_next-p_start)),Point((p1-p0-theta)/float(p_next**2-p_start**2),0))
        if fcs.isempty():
            #define the space between first l,u
            g_new=Polygon()
            g_new.space(l,u)
        elif fcs.is_space:
            # find intersection between the four first lines
            b1,q1=intersect(l.points[0],l.points[1],fcs.lower.points[0],fcs.lower.points[1])
            b2,q2=intersect(l.points[0],l.points[1],fcs.upper.points[0],fcs.upper.points[1])
            b3,q3=intersect(u.points[0],u.points[1],fcs.upper.points[0],fcs.upper.points[1])
            b4,q4=intersect(u.points[0],u.points[1],fcs.lower.points[0],fcs.lower.points[1])
            g_new = Polygon() #empty polygon
            if b1 and b2 and b3 and b4:
                g_new.add_vertex(q1)
                g_new.add_vertex(q2)
                g_new.add_vertex(q3)
                g_new.add_vertex(q4)
        else:
            # u1=[]
            # l1=[]
            # poly=[]
            # for p in u.points:
            #     u1.append([p.r,p.i])
            # for p in l.points:
            #     l1.append([p.r,p.i])
            # for p in fcs.vertices:
            #     poly.append([p.r,p.i])
            # poly.append(poly[0])
            # u1=np.array(u1)
            # l1=np.array(l1)
            # poly=np.array(poly)
            # x1 = u1[0, 0]
            # y1 = u1[0, 1]
            # x2 = u1[1, 0]
            # y2 = u1[1, 1]
            # x_1 = l1[0, 0]
            # y_1 = l1[0, 1]
            # x_2 = l1[1, 0]
            # y_2 = l1[1, 1]
            # line_eqn1 = lambda x: ((y2 - y1) / (x2 - x1)) * (x - x1) + y1
            # line_eqn2 = lambda x: ((y_2 - y_1) / (x_2 - x_1)) * (x - x_1) + y_1
            # xrange = np.arange(min(poly[:,0]),max(poly[:,0]),abs(abs(max(poly[:,0]))-abs(min(poly[:,0])))/len(poly[:,0]))
            # plt.plot(poly[:, 0], poly[:, 1], '-o')
            # plt.plot(xrange, [line_eqn1(x) for x in xrange], color='g', linestyle='-')
            # plt.plot(xrange, [line_eqn2(x) for x in xrange], color='r', linestyle='-')

            #find the intersection between the polygon and l,u
            g_lower=polygon_cut(fcs,l,False)
            g_new=polygon_cut(g_lower,u,True)
        return g_new

    elif fj == 'linear': #To implement
        #construct two interval endpoints l and u
        p0 = P[p_start]
        p1 = P[p_next]
        u=Point((p1-p0+theta)/float(p_next-p_start),0)
        l=Point((p1-p0-theta)/float(p_next-p_start),0)
        if fcs.isempty():
            g_new=Polygon()
            g_new.interval(l,u)
        elif fcs.is_interval:
            #find intersection of two intervals
            g_new = Polygon()
            if (fcs.l.real() <= u.real()) and (l.real()<= fcs.u.real()):
                g_new.interval(Point(max(fcs.l.real(),l.real()),0),Point(min(fcs.u.real(),u.real()),0))
        return g_new
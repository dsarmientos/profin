import os
import sys

import numpy as np
import mahotas
import pymorph
import pylab
from scipy.cluster.vq import kmeans,vq
from scipy import ndimage

DEBUG = False


R, G, B = range(3)

def main(infile):
    img = mahotas.imread(infile)
    filename = os.path.splitext(os.path.basename(infile))[0]

    f, blue_component, combined = segment(img, filename)
    count(img, f, combined, blue_component, filename)

def segment_kmeans(img, k):
    f = img.flatten()
    centroids, _ = kmeans(f,k)
    while centroids.size != k:
        centroids, _ = kmeans(f,k)
    centroids.sort()
    clustered, _ = vq(f, centroids)
    return clustered.reshape(img.shape)

def remove_by_size(labeled, min_size, max_size):
    assert min_size < max_size
    return remove_too_small(
        remove_too_big(labeled, max_size),
        min_size)

def remove_too_small(labeled, min_size):
    sizes = mahotas.labeled.labeled_size(labeled)
    too_small = np.where(sizes < min_size)
    return mahotas.labeled.remove_regions(labeled, too_small)

def remove_too_big(labeled, max_size):
    sizes = mahotas.labeled.labeled_size(labeled)
    too_big = np.where(sizes > max_size)
    return mahotas.labeled.remove_regions(labeled, too_big)

def labeled_to_binary(labeled, copy=False):
    if not copy:
        labeled[labeled != 0] = 1
    else:
        c = np.copy(labeled)
        c[c != 0] = 1
        return c

def segment(img, filename, min_size=1500, max_size=18000):
    blue_component = img[:,:,B]

    pylab.gray()
    k = 3
    f = ndimage.gaussian_filter(blue_component, 12)

    clustered = segment_kmeans(f, k)
    clustered[clustered == k-1] = 0
    mask = ndimage.binary_fill_holes(clustered)

    if DEBUG:
        mahotas.imsave('00masknoholes-%s.jpg' % filename, mask)

    masked = f * mask

    if DEBUG:
        mahotas.imsave('01masked-%s.jpg' % filename, masked)

    k = 4
    clustered2 = segment_kmeans(masked, k)

    if DEBUG:
        mahotas.imsave('02kmeans2-%s.jpg' % filename, clustered2)

    clustered2[(clustered2 != k-2)] = 0
    clustered2[(clustered2 == k-2)] = 1

    if DEBUG:
        mahotas.imsave('03kmeans2f-%s.jpg' % filename, clustered2)

    clustered2 = ndimage.binary_fill_holes(clustered2)

    if DEBUG:
        mahotas.imsave('04kmeans2fnoholes-%s.jpg' % filename, clustered2)

    labeled, _  = mahotas.label(mask)
    labeled1 = remove_by_size(labeled, min_size, max_size-2000)

    if DEBUG:
        mahotas.imsave('05labeled1-%s.jpg' % filename, labeled)
        mahotas.imsave('07labeled1f-%s.jpg' % filename, labeled1)

    labeled, _  = mahotas.label(clustered2)
    labeled2 = remove_by_size(labeled, min_size, max_size)

    if DEBUG:
        mahotas.imsave('08labeled2f-%s.jpg' % filename, labeled)
        mahotas.imsave('10labeled2f-%s.jpg' % filename, labeled2)

    combined = labeled1 + labeled2

    labeled_to_binary(combined)
    if DEBUG:
        mahotas.imsave('11combined-%s.jpg' % filename, combined)

    combined = ndimage.binary_fill_holes(combined)

    if DEBUG:
        mahotas.imsave('12combined_noholes-%s.jpg' % filename, combined)

    mahotas.imsave('output/%s-combined.jpg' % filename, combined)
    return f, blue_component, combined

def count(img, f, combined, blue_component, filename):
    borders = mahotas.labeled.borders(mahotas.label(combined)[0])

    cells = f * combined
    cells[cells == 0] = 255

    if DEBUG:
        mahotas.imsave('13cellsw-%s.jpg' % filename, cells)

    rmin = mahotas.regmin(cells)
    seeds, nr_nuclei = mahotas.label(rmin)

    if DEBUG:
        mahotas.imsave(
            '14gscale-final-%s.jpg' % filename,
            pymorph.overlay(blue_component, rmin,
                        borders)
        )

    img2 = np.copy(img)
    img2[borders] = [0,0,0]
    img2[rmin] = [5,250,42]
    if DEBUG:
        mahotas.imsave('15no-wshed-final-%s.jpg' % (filename), img2)

    #watershed
    gradient = ndimage.morphology.morphological_gradient(combined, size=(3,3))
    gradient = gradient.astype(np.uint8)
    if DEBUG:
        mahotas.imsave('16gradient-%s.jpg' % filename, gradient)
    wshed, lines = mahotas.cwatershed(gradient, seeds, return_lines=True)


    pylab.jet()

    if DEBUG:
        mahotas.imsave('17wshed-%s.jpg', wshed)

    ncells =  len(np.unique(wshed)) - 1
    print '%d cells.' % ncells
    borders = mahotas.labeled.borders(wshed)

    img[borders] = [0,0,0]
    img[rmin] = [5,250,42]
    mahotas.imsave('output/%s-output-%dcells.jpg' % (filename, ncells), img)
    return ncells, img

if __name__ == '__main__':
    try:
        assert len(sys.argv) == 2
        infile = sys.argv[1]
    except Exception:
        print 'Usage %s <infile>' % __file__
    else:
        main(infile)

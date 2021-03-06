import os
import sys

import numpy as np
import mahotas
import pymorph
import pylab
from scipy.cluster.vq import kmeans,vq
from scipy import ndimage

DEBUG = True


R, G, B = range(3)

def main(infile):
    img = mahotas.imread(infile)
    infile = os.path.splitext(
        os.path.basename(infile))[0]
    blue_component = img[:,:,B]

    pylab.gray()
    k = 3
    f = ndimage.gaussian_filter(blue_component, 12)
    if DEBUG:
        print 'Procesando imagen %s usando canal azul' % (infile)
        mahotas.imsave('00%s-input.jpg' % infile, f)

    clustered = segment_kmeans(f, k)
    clustered[clustered == k-1] = 0
    mask = ndimage.binary_fill_holes(clustered)

    if DEBUG:
        print 'Segmentacion inicial k-means con k=%d' % k
        mahotas.imsave('01kmeans1%s.jpg' % infile, mask)

    masked = f * mask

    if DEBUG:
        mahotas.imsave('02masked%s.jpg' % infile, masked)

    k = 4
    clustered2 = segment_kmeans(masked, k)

    if DEBUG:
        print 'Resegmentacion k-means con k=%d' % k
        mahotas.imsave('03kmeans2%s.jpg' % infile, clustered2)

    clustered2[(clustered2 != k-2)] = 0
    clustered2[(clustered2 == k-2)] = 1

    if DEBUG:
        mahotas.imsave('04kmeans2binary%s.jpg' % infile, clustered2)

    clustered2 = ndimage.binary_fill_holes(clustered2)

    labeled, _  = mahotas.label(mask)
    if DEBUG:
        print 'Etiquetando imagen segmentacion inicial k-means'
        mahotas.imsave('05kmeans2noholes%s.jpg' % infile, clustered2)
        mahotas.imsave('06kmeans2labeled%s.jpg' % infile, labeled)
        while True:
            min_max = raw_input('label1 min,max? ')
            try:
                min_max = min_max.strip().split(',')
                min_ = int(min_max[0])
                max_ = int(min_max[1])
            except:
                break
            labeled1 = remove_by_size(labeled, min_, max_)
            mahotas.imsave('07labeled1f%d,%d%s.jpg' % (min_, max_, infile), labeled1)

    labeled, _  = mahotas.label(clustered2)
    labeled2 = remove_by_size(labeled, 1600, 23000)

    if DEBUG:
        print 'Etiquetando imagen re-segmentacion k-means'
        mahotas.imsave('08labeled2f%s.jpg' % infile, labeled)
        mahotas.imsave('09labeled2f%s.jpg' % infile, labeled2)

    combined = labeled1 + labeled2

    labeled_to_binary(combined)
    if DEBUG:
        mahotas.imsave('10combined%s.jpg' % infile, combined)

    combined = ndimage.binary_fill_holes(combined)

    if DEBUG:
        mahotas.imsave('11combined_noholes%s.jpg' % infile, combined)

    borders = mahotas.labeled.borders(mahotas.label(combined)[0])

    cells = f * combined
    cells[cells == 0] = 255

    if DEBUG:
        mahotas.imsave('12maskedcellsw%s.jpg' % infile, cells)

    rmin = mahotas.regmin(cells)
    seeds, nr_nuclei = mahotas.label(rmin)

    if DEBUG:
        mahotas.imsave(
            '13gscale-final%s.jpg' % infile,
            pymorph.overlay(blue_component, rmin,
                        borders)
        )

    img2 = np.copy(img)
    img2[borders] = [0,0,0]
    img2[rmin] = [5,250,42]
    mahotas.imsave('14%s-outputcells.jpg' % (infile), img2)

    #watershed
    gradient = ndimage.morphology.morphological_gradient(combined, size=(3,3))
    gradient = gradient.astype(np.uint8)
    if DEBUG:
        print 'Watershed'
        mahotas.imsave('15%s-gradient.jpg' % infile, gradient)
    wshed, lines = mahotas.cwatershed(gradient, seeds, return_lines=True)


    pylab.jet()

    if DEBUG:
        mahotas.imsave('16wshed.jpg', wshed)

    ncells =  len(np.unique(wshed)) - 1
    print '%d cells.' % ncells
    borders = mahotas.labeled.borders(wshed)

    img[borders] = [0,0,0]
    img[rmin] = [5,250,42]
    mahotas.imsave('17%s-output-%dcells.jpg' % (infile, ncells), img)

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

if __name__ == '__main__':
    try:
        assert len(sys.argv) == 2
        infile = sys.argv[1]
    except Exception:
        print 'Usage %s <infile>' % __file__
    else:
        main(infile)

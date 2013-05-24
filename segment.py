import sys
import ipdb

import numpy as np
import mahotas
import pymorph
import pylab
from scipy.cluster.vq import kmeans,vq
from scipy import ndimage


R, G, B = range(3)

def main(infile):
    img = mahotas.imread(infile)
    blue_component = img[:,:,B]


    pylab.gray()
    k = 3
    f = ndimage.gaussian_filter(blue_component, 12)
    mahotas.imsave('000blue%s.jpg' % k, f)

    clustered = segment_kmeans(f, k)
    clustered[clustered == k-1] = 0
    mask = clustered.reshape(f.shape)
    mask = ndimage.binary_fill_holes(mask)
    mahotas.imsave('00masknoholes%s.jpg' % k, mask)

    masked = f * mask
    mahotas.imsave('01masked%s.jpg' % k, masked)

    k = 4
    clustered2 = segment_kmeans(masked, k)
    clustered2 = clustered2.reshape(masked.shape)
    mahotas.imsave('02kmeans2%s.jpg' % k, clustered2)

    clustered2[(clustered2 != k-2)] = 0
    clustered2[(clustered2 == k-2)] = 1
    mahotas.imsave('03kmeans2f%s.jpg' % k, clustered2)
    clustered2 = ndimage.binary_fill_holes(clustered2)
    mahotas.imsave('04kmeans2fnoholes%s.jpg' % k, clustered2)

    labeled, _  = mahotas.label(mask)
    mahotas.imsave('05labeled1%s.jpg' % k, labeled)
    labeled1 = remove_too_big(labeled, 16000)
    mahotas.imsave('06labeled1_notobig%s.jpg' % k, labeled1)
    labeled1 = remove_too_small(labeled1, 1500)
    mahotas.imsave('07labeled1f%s.jpg' % k, labeled1)

    labeled, _  = mahotas.label(clustered2)
    mahotas.imsave('08labeled2%s.jpg' % k, labeled)
    labeled2 = remove_too_big(labeled, 18000)
    mahotas.imsave('09labeled2_notobig%s.jpg' % k, labeled2)
    labeled2 = remove_too_small(labeled2, 1500)
    mahotas.imsave('10labeled2f%s.jpg' % k, labeled2)

    combined = labeled1 + labeled2
    labeled_to_binary(combined)
    mahotas.imsave('11combined%s.jpg' % k, combined)
    combined = ndimage.binary_fill_holes(combined)
    mahotas.imsave('12combined_noholes%s.jpg' % k, combined)

    borders = mahotas.labeled.borders(mahotas.label(combined)[0])
    mahotas.imsave('12aborders%s.jpg' % k, borders)

    cells = f * combined
    mahotas.imsave('13cells%s.jpg' % k, cells)

    cells[cells == 0] = 255
    mahotas.imsave('14cellsw%s.jpg' % k, cells)

    rmin = mahotas.regmin(cells)
    seeds, nr_nuclei = mahotas.label(rmin)
    mahotas.imsave('15overlay.jpg', pymorph.overlay(blue_component, rmin))
    mahotas.imsave('16seeds.jpg', seeds)
    final = np.zeros(borders.shape)
    final[borders] = 1
    mahotas.imsave('16aborders.jpg', final)
    mahotas.imsave('17foverlay.jpg', final + seeds)
    mahotas.imsave('18foverlay.jpg', final + seeds)
    mahotas.imsave(
        '19final.jpg',
        pymorph.overlay(blue_component, rmin,
                        borders)
    )
    img2 = np.copy(img)
    img2[borders] = [0,0,0]
    img2[rmin] = [5,250,42]
    mahotas.imsave('20t.jpg', img2)

    #watershed
    gradient = ndimage.morphology.morphological_gradient(final, size=(3,3))
    gradient = gradient.astype(np.uint8)
    mahotas.imsave('21gradient.jpg', gradient)
    wshed, lines = mahotas.cwatershed(gradient, seeds, return_lines=True)
    print '%d cells.' % len(np.unique(wshed))
    pylab.jet()
    mahotas.imsave('22wshed.jpg', wshed)
    borders = mahotas.labeled.borders(wshed)
    mahotas.imsave('23labeled.jpg', borders)
    img2 = np.copy(img)
    img2[borders] = [0,0,0]
    mahotas.imsave('24t.jpg', img2)
    img2 = np.copy(img)
    img2[lines] = [0,0,0]
    mahotas.imsave('25t.jpg', img2)



def segment_kmeans(img, k):
    f = img.flatten()
    centroids, _ = kmeans(f,k)
    while centroids.size != k:
        centroids, _ = kmeans(f,k)
    centroids.sort()
    clustered, _ = vq(f, centroids)
    return clustered

def remove_labeles(labeled, min_size, max_size):
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

import sys
import ipdb

import numpy as np
import mahotas
import pylab
from scipy.cluster.vq import kmeans,vq
from scipy import ndimage


R, G, B = range(3)

def main(infile):
    k = 3
    img = mahotas.imread(infile)
    blue_component = img[:,:,B]
    f = ndimage.gaussian_filter(blue_component, 12)
    clustered = segment_kmeans(f, k)
    clustered[clustered == k-1] = 0
    print np.unique(clustered)
    mask = clustered.reshape(f.shape)
    mahotas.imsave('mask%s.jpg' % k, mask)

    pylab.gray()
    masked = f * mask
    mahotas.imsave('masked%s.jpg' % k, masked)

    k = 4
    clustered2 = segment_kmeans(masked, k)
    mahotas.imsave('kmeans2%s.jpg' % k, clustered2.reshape(f.shape))

    # for i in xrange(k):
    #     t = np.copy(clustered2)
    #     t[(t != i)] = 0
    #     mahotas.imsave('k%s.jpg' % i, t.reshape(f.shape))

    # Sin el mas claro, y los dos mas oscuros
    clustered2[clustered2 != k-2] = 0
    clustered2[clustered2 == k-2] = 1
    print np.unique(clustered2)
    clustered2 = clustered2.reshape(f.shape)
    mahotas.imsave('kmeans2f%s.jpg' % k, clustered2)
    # return

    labeled, _  = mahotas.label(mask)
    sizes = mahotas.labeled.labeled_size(labeled)
    too_big = np.where(sizes > 30000)
    too_small = np.where(sizes < 1000)
    labeled1 = mahotas.labeled.remove_regions(labeled, too_big)
    labeled1[labeled1 != 0] = 1
    labeled1 = labeled1.reshape(f.shape)
    mahotas.imsave('labeled1%s.jpg' % k, labeled1)

    labeled, _  = mahotas.label(clustered2)
    sizes = mahotas.labeled.labeled_size(labeled)
    too_small = np.where(sizes < 1000)
    too_big = np.where(sizes > 20000)
    labeled2 = mahotas.labeled.remove_regions(labeled, too_big)
    labeled2[labeled2 != 0] = 1
    labeled2 = labeled2.reshape(f.shape)
    mahotas.imsave('labeled2%s.jpg' % k, labeled2)

    comb = labeled1 + labeled2
    print np.unique(comb)
    for i in np.unique(comb):
        t = np.copy(comb)
        comb[(comb != i)] = 0
        mahotas.imsave('comb%s.jpg' % i, t.reshape(f.shape))
    mahotas.imsave('comb%s.jpg' % k, labeled2)



def segment_kmeans(img, k):
    f = img.flatten()
    centroids, _ = kmeans(f,k)
    centroids.sort()
    clustered, _ = vq(f, centroids)
    return clustered

if __name__ == '__main__':
    try:
        assert len(sys.argv) == 2
        infile = sys.argv[1]
    except Exception:
        print 'Usage %s <infile>' % __file__
    else:
        main(infile)

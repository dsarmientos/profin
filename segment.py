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

    clustered2 = segment_kmeans(masked, 4)
    clustered2 = clustered2.reshape(f.shape)
    mahotas.imsave('kmeans2%s.jpg' % k, clustered2)

    # Sin el mas claro, y los dos mas oscuros
    k = 4
    clustered2[(clustered2 != k-2)] = 0
    clustered2[(clustered2 == k-2)] = 1
    mahotas.imsave('kmeans2f%s.jpg' % k, clustered2)

    labeled, _  = mahotas.label(mask)
    print np.unique(labeled), labeled.shape
    sizes = mahotas.labeled.labeled_size(labeled)
    too_big = np.where(sizes > 15000)
    labeled1 = mahotas.labeled.remove_regions(labeled, too_big)
    mahotas.imsave('labeled1%s.jpg' % k, labeled1)

    labeled, _  = mahotas.label(clustered2)
    sizes = mahotas.labeled.labeled_size(labeled)
    too_big = np.where(sizes > 15000)
    labeled2 = mahotas.labeled.remove_regions(labeled, too_big)
    mahotas.imsave('labeled2%s.jpg' % k, labeled2)
    return





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

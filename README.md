# Filtering Speed Test
## Usage

```
> python .\main.py -h
usage: Filtering Speed Test [-h] [--doh-upstream DOH_UPSTREAM] --url URL [--figure FIGURE] --num NUM

A simple tester that measures latency to an upstream L7 filtering service.

optional arguments:
  -h, --help            show this help message and exit
  --doh-upstream DOH_UPSTREAM
                        The upstream to use for DNS-over-HTTPS (DoH) tests.
  --url URL             The URL to use for this test.
  --figure FIGURE       Path to output final distribution to.
  --num NUM, -n NUM     Number of times to run domain.
```

## DNS-over-HTTPS (DoH) Examples
### With the default Cloudflare upstream:

```
> python .\main.py --url https://msn.com -n 1 --figure latency.msn.cloudflare.png
```

### With your own preferred upstream:

```
> python .\main.py --url https://www.youtube.com -n 1 --doh-upstream https://rcsv.ddr.ultradns.com/yoink --figure latency.youtube.vercara.png
```
import argparse, os, time
from services.scraper.core.scheduler import parse_scope
from services.scraper.runners import daily as daily_runner
from services.scraper.runners import bootstrap as bootstrap_runner
from services.scraper.runners import special as special_runner

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["daily","bootstrap","special"], required=True)
    parser.add_argument("--scope", required=True, help='e.g. "federal:*" or "provincial:on:representatives"')
    parser.add_argument("--since", default=None)
    args = parser.parse_args()

    tier, code, entity = parse_scope(args.scope)
    start = time.time()
    if args.mode=="daily":
        daily_runner.run(tier, code, entity)
    elif args.mode=="bootstrap":
        bootstrap_runner.run(tier, code, entity, since=args.since)
    else:
        special_runner.run(tier, code, entity)
    print(f"[scrapers] {args.mode} {args.scope} finished in {time.time()-start:.2f}s")

if __name__ == "__main__":
    main()
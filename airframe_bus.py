#!/usr/bin/python3
import lxml.html
import requests
import argparse
import sys

class horaire():
    def __init__(self):
        self.passages = None
        self.stops = {}

    def get_horaires(self, url):
        r = requests.get(url)
        tree = lxml.html.fromstring(r.text)
        node_stop = tree.xpath( ''
                + '//div[@id="prochains_passages"]'
                + '/fieldset'
                + '/div[@class="line_details"]/span')
        stop_name = node_stop[0].text
        nodes = tree.xpath(
                '//div[@id="prochains_passages"]/fieldset/table/tbody/tr')
        passages = []
        for passage in nodes:
            tds = [x.text for x in passage.xpath("td")]
            if len(tds) < 2:
                passages += [{"dest" : tds[0], "time" : 0}]
                continue
            try:
                t = tds[1].split()[0]
                int(t)
                passages += [{"dest" : tds[0], "time" : t}]
            except ValueError:
                if tds[1] in [ "A l'approche", "A l'arret"] :
                    tds[1] = "0"
                passages += [{"dest" : tds[0], "time" : tds[1]}]
        self.stops[stop_name] = passages
        return stop_name

    def horaires2string_list(self, stop_names=None, print_stops=None):
        if not stop_names:
            return None
        ret = []
        base_stop = "=== {name} ==="
        base_str = "{dest} {time}"
        for stop in stop_names:
            passages = self.stops[stop]
            if print_stops:
                ret += [base_stop.format(name=stop)]
            ret += [base_str.format(dest=p["dest"], time=p["time"]) for p
                    in sorted(passages, key=lambda x:int(x["time"]) if
                        x["time"].isdigit() else sys.maxsize)]
        return ret

def main():
    parser = argparse.ArgumentParser(description='Get Ratp Bus Time')
    parser.add_argument("urls", nargs='+', help="URLs of buses stop")
    parser.add_argument("-j", "--print_json", action="store_true",
        help="Output as json.")
    parser.add_argument("-s", "--print_stops", action="store_true",
        help="Also print stops. Useless when used with -j")
    args = parser.parse_args()
    stops = []
    h = horaire()
    for url in args.urls:
        stops += [h.get_horaires(url)]
    if args.print_json:
        print(h.stops)
        return 0
    print(*h.horaires2string_list(stop_names=stops,
        print_stops=args.print_stops), sep='\n')

if __name__ == "__main__" :
    main()

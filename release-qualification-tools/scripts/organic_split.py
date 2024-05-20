from exrex import getone
from scripts.steps.orderflow.setup import prepare_orderflow_data
from src.api.takeoff.distiller import Distiller
from src.api.takeoff.ims import IMS
from src.api.takeoff.oms import OMS
from src.api.takeoff.rint import RInt
from src.api.takeoff.tsc import TSC
from src.config.config import Config, get_token, get_config, get_config_date
from src.utils.place_order import place_order
from src.utils.console_printing import bold

"""
 python3 -m scripts.organic_split --r <retailer_name> --e <env> --l <location> --d <day> --h<hour>
 e.g.
  python3 -m scripts.organic_split --r abs --e qai --l 0068 --d 1 --h 2 , which is 1 day from today and 2 hours
"""
order_links = []
*config, day, hour = get_config()
cfg = Config(*config)
custom_date = get_config_date(day, hour)
requested_retailer = cfg.retailer
for t in range(3):
    try:
        token = get_token(retailer=cfg.retailer, env=cfg.env)
        cfg = Config(
            retailer=cfg.retailer,
            env=cfg.env,
            location_code_tom=cfg.location_code_tom,
            token=cfg.token,
        )
        ims = IMS(cfg)
        distiller = Distiller(cfg)
        tsc = TSC(cfg)
        rint = RInt(cfg)
        oms = OMS(cfg)

        test_data = prepare_orderflow_data(
            ims=ims,
            distiller=distiller,
            tsc=tsc,
            retailer=cfg.retailer,
            osr_products_qty=1,
        )

        service_window_start = (
            custom_date[:14] + str(int(custom_date[14:16]) + 1) + custom_date[16:]
        )
        stage_by_datetime = custom_date

        print(bold("Organic split stage_by_datetime: ") + bold(stage_by_datetime))
        print(bold("Organic split service_window_start: ") + bold(service_window_start))

        order_id = place_order(
            ims=ims,
            oms=oms,
            rint=rint,
            retailer=cfg.retailer,
            products=test_data["all_products"],
            order_id=getone("os[0-9]{13}"),
            store_id=test_data["store_id"],
            spoke_id=test_data["spoke_id"],
            stage_by_datetime=service_window_start,
            service_window_start=service_window_start,
            print_body=False,
        )

        order_link = cfg.tom_ui_url(rel=f"orders/details/?id={order_id}")
        order_links.append(order_link)
    except Exception as e:
        print(e)

for link in sorted(order_links):
    print(link)

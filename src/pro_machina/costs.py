from __future__ import annotations

from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from .durations import Duration
from .measures import SizedDimension

if TYPE_CHECKING:
    from .problem.consumables import Consumable
    from .problem.machines import _Machine
    from .problem.products import _Product


class CurrencyRefresh(StrEnum):
    EVERY_RUN = "EVERY RUN"
    HOURLY = "HOURLY"
    DAILY = "DAILY"
    MONTHLY = "MONTHLY"
    ONCE = "ONCE"


class Currency(StrEnum):
    BASE = "Set to base currency specified in Config"
    NON = "Fictional currency where everything is a 1:1 conversion"
    AED = "United Arab Emirates Dirham"
    AFN = "Afghan Afghani"
    ALL = "Albanian Lek"
    AMD = "Armenian Dram"
    ANG = "Netherlands Antillean Guilder"
    AOA = "Angolan Kwanza"
    ARS = "Argentine Peso"
    AUD = "Australian Dollar"
    AWG = "Aruban Florin"
    AZN = "Azerbaijani Manat"
    BAM = "Bosnia and Herzegovina Convertible Mark"
    BBD = "Barbadian Dollar"
    BDT = "Bangladeshi Taka"
    BGN = "Bulgarian Lev"
    BHD = "Bahraini Dinar"
    BIF = "Burundian Franc"
    BMD = "Bermudian Dollar"
    BND = "Brunei Dollar"
    BOB = "Bolivian Boliviano"
    BOV = "Mvdol"
    BRL = "Brazilian Real"
    BSD = "Bahamian Dollar"
    BTN = "Ngultrum"
    BWP = "Pula"
    BYN = "Belarusian Ruble"
    BZD = "Belize Dollar"
    CAD = "Canadian Dollar"
    CDF = "Congolese Franc"
    CHF = "Swiss Franc"
    CLF = "Unidad de Fomento"
    CLP = "Chilean Peso"
    CNY = "Yuan Renminbi"
    COP = "Colombian Peso"
    CRC = "Costa Rican Colon"
    CUC = "Peso Convertible"
    CUP = "Cuban Peso"
    CVE = "Cabo Verde Escudo"
    CZK = "Czech Koruna"
    DJF = "Djibouti Franc"
    DKK = "Danish Krone"
    DOP = "Dominican Peso"
    DZD = "Algerian Dinar"
    EGP = "Egyptian Pound"
    ETB = "Ethiopian Birr"
    ERN = "Eritrean Nakfa"
    EUR = "Euro"
    FJD = "Fiji Dollar"
    FKP = "Falkland Islands Pound"
    GBP = "Pound sterling"
    GEL = "Georgian Lari"
    GHS = "Ghana Cedi"
    GIP = "Gibraltar Pound"
    GMD = "Gambian Dalasi"
    GNF = "Guinean Franc"
    GTQ = "Guatemalan Quetzal"
    GYD = "Guyana Dollar"
    HKD = "Hong Kong Dollar"
    HNL = "Honduran Lempira"
    HTG = "Haitian Gourde"
    HUF = "Hungarian Forint"
    IDR = "Indonesian Rupiah"
    ILS = "New Israeli Sheqel"
    INR = "Indian Rupee"
    IQD = "Iraqi Dinar"
    IRR = "Iranian Rial"
    ISK = "Iceland Krona"
    JEP = "Jersey Pound"
    JMD = "Jamaican Dollar"
    JOD = "Jordanian Dinar"
    JPY = "Japanese Yen"
    KES = "Kenyan Shilling"
    KGS = "Kyrgyz Som"
    KHR = "Cambodian Riel"
    KMF = "Comorian Franc"
    KPW = "North Korean Won"
    KRW = "South Korean Won"
    KWD = "Kuwaiti Dinar"
    KYD = "Cayman Islands Dollar"
    KZT = "Kazakhstani Tenge"
    LAK = "Lao Kip"
    LBP = "Lebanese Pound"
    LKR = "Sri Lanka Rupee"
    LRD = "Liberian Dollar"
    LSL = "Lesotho Loti"
    LYD = "Libyan Dinar"
    MAD = "Moroccan Dirham"
    MDL = "Moldovan Leu"
    MGA = "Malagasy Ariary"
    MKD = "Macedonian Denar"
    MMK = "Burmese Kyat"
    MNT = "Mongolian Tögrög"
    MOP = "Macanese Pataca"
    MRU = "Mauritanian Ouguiya"
    MUR = "Mauritanian Rupee"
    MVR = "Maldivian Rufiyaa"
    MWK = "Malawi Kwacha"
    MXN = "Mexican Peso"
    MXV = "Mexican Unidad de Inversion (UDI)"
    MYR = "Malaysian Ringgit"
    MZN = "Mozambique Metical"
    NAD = "Namibia Dollar"
    NGN = "Nigerian Naira"
    NIO = "Cordoba Oro"
    NOK = "Norwegian Krone"
    NPR = "Nepalese Rupee"
    NZD = "New Zealand Dollar"
    OMR = "Rial Omani"
    PAB = "Panamanian Balboa"
    PEN = "Peruvian Sol"
    PGK = "Papua New Guinean Kina"
    PHP = "Philippine Peso"
    PKR = "Pakistan Rupee"
    PLN = "Polish Zloty"
    PYG = "Paraguayan Guarani"
    QAR = "Qatari Rial"
    RON = "Romanian Leu"
    RSD = "Serbian Dinar"
    RUB = "Russian Ruble"
    RWF = "Rwanda Franc"
    SAR = "Saudi Riyal"
    SBD = "Solomon Islands Dollar"
    SCR = "Seychelles Rupee"
    SDG = "Sudanese Pound"
    SEK = "Swedish Krona"
    SGD = "Singapore Dollar"
    SHP = "Saint Helena Pound"
    SLE = "Sierra Leonean Leone"
    SLL = "Leone"
    SOS = "Somali Shilling"
    SRD = "Surinam Dollar"
    STN = "São Tomé and Príncipe Dobra"
    SSP = "South Sudanese Pound"
    SYP = "Syrian Pound"
    SZL = "Swazi Lilangeni"
    THB = "Thai Baht"
    TJS = "Tajikistani Somoni"
    TMT = "Turkmenistan New Manat"
    TND = "Tunisian Dinar"
    TOP = "Tongan paʻanga"
    TRY = "Turkish Lira"
    TTD = "Trinidad and Tobago Dollar"
    TWD = "New Taiwan Dollar"
    TZS = "Tanzanian Shilling"
    UAH = "Ukrainian Hryvnia"
    UGX = "Uganda Shilling"
    USD = "United States Dollar"
    UYU = "Peso Uruguayo"
    UZS = "Uzbekistan Sum"
    VED = "Bolívar Soberano"
    VES = "Bolívar Soberano"
    VND = "Vietnamese Dong"
    VUV = "Vanuatu Vatu"
    WST = "Samoan Tālā"
    XAF = "CFA Franc BEAC"
    XCD = "East Caribbean Dollar"
    XDR = "SDR (Special Drawing Right)"
    XOF = "CFA Franc BCEAO"
    XPF = "CFP Franc"
    YER = "Yemeni Rial"
    ZAR = "South African Rand"
    ZMW = "Zambian Kwacha"
    ZWL = "Zimdollar"

    @staticmethod
    def list_all():
        print("CODE\tNAME")
        print("****\t****")
        for row in Currency.__members__.items():
            print(f"{row[0]}\t{row[1]}")


class _RunningCost:
    def __init__(
        self,
        value: float | str | Decimal,
        per: Duration,
        products: _Product | list[_Product] | None,
        currency: Currency = Currency.BASE,
        _machine: _Machine | None = None,
    ) -> None:
        self.value = Decimal(value)
        self.currency = currency
        self.per = per
        self._machine = _machine
        self.products = None  # products

    def _set_machine(self, machine: _Machine):
        if self._machine is None:
            # inherit all of the products made by the machine by default
            self.products = list(machine._products.values())

        self._machine = machine

    def check_products_being_made(self) -> bool:
        if self._machine is None:
            raise ValueError(
                f"Machine has not been set for this cost {type(self).__name__}"
            )
        made_prods = set(
            [item["product"]._id for item in self._machine._products.values()]
        )
        for prod in self.products:
            if prod._id not in made_prods:
                raise ValueError(
                    "Attempted to set a labour cost for product:"
                    f" {prod.name} that is not being made by machine:"
                    f" {self._machine.name}."
                )
        return True


class LabourCost(_RunningCost):
    """Class to track the labour costs of producing products.

    Parameters
    ----------
    value : float | str | Decimal
        The financial value representing the unit cost e.g. £15.
    per : Duration
        The period of time over which the unit cost is realised e.g. 1 hour.
    products : _Product | list[_Product] | None
        The product or list of products that this labour cost applies to. For
        example, a machine may be able to produce 10 different products but six
        of those products can be produced by a single machine opertor whilst
        three others require two machine operators and the final one requires
        a third operator. By default, this is None, which will apply a fixed
        cost across all products that this machine can produce, without having
        to set the value on a per-product basis.
    currency : Currency, optional
        The currency the labour cost is realised in, by default Currency.BASE.
    """

    def __init__(
        self,
        value: float | str | Decimal,
        per: Duration,
        products: _Product | list[_Product] | None,
        currency: Currency = Currency.BASE,
        _machine: _Machine | None = None,
    ) -> None:
        super().__init__(
            value=value,
            per=per,
            products=products,
            currency=currency,
            _machine=_machine,
        )


class ProductionCost(_RunningCost):
    """Class to track the non-labour costs of producing products.

    Parameters
    ----------
    value : float | str | Decimal
        The financial value representing the unit cost e.g. £15.
    per : Duration
        The period of time over which the unit cost is realised e.g. 1 hour.
    products : _Product | list[_Product] | None
        The product or list of products that this labour cost applies to. For
        example, a machine may be able to produce 10 different products but six
        of those products can be produced by a single machine opertor whilst
        three others require two machine operators and the final one requires
        a third operator. By default, this is None, which will apply a fixed
        cost across all products that this machine can produce, without having
        to set the value on a per-product basis.
    currency : Currency, optional
        The currency the labour cost is realised in, by default Currency.BASE.
    """

    def __init__(
        self,
        value: float | str | Decimal,
        per: Duration,
        products: _Product | list[_Product] | None,
        currency: Currency = Currency.BASE,
        _machine: _Machine | None = None,
    ) -> None:
        super().__init__(
            value=value,
            per=per,
            products=products,
            currency=currency,
            _machine=_machine,
        )


class _Capital:
    def __init__(
        self,
        gross_value: float | str | Decimal | None = None,
        net_value: float | str | Decimal | None = None,
        currency: Currency = Currency.BASE,
    ) -> None:

        if gross_value is None and net_value is None:
            raise ValueError(
                "A minimum of either a gross_value or net_value must be"
                " specified"
            )

        self.gross_value = Decimal(gross_value)
        self.net_value = Decimal(net_value)
        self.currency = currency


class PurchaseCost(_Capital):
    def __init__(
        self,
        per: SizedDimension,
        gross_value: float | str | Decimal | None = None,
        net_value: float | str | Decimal | None = None,
        currency: Currency = Currency.BASE,
        consumable: Consumable | None = None,
    ) -> None:
        super().__init__(
            gross_value=gross_value, net_value=net_value, currency=currency
        )
        self.per = per
        self.consumable = consumable

    def _set_consumable(self, consumable: Consumable):
        self.consumable = consumable


class OrderlineValue(_Capital):
    def __init__(
        self,
        product: _Product,
        gross_value: float | str | Decimal | None = None,
        net_value: float | str | Decimal | None = None,
        currency: Currency = Currency.BASE,
    ) -> None:
        super().__init__(
            gross_value=gross_value, net_value=net_value, currency=currency
        )
        self.product = product


class SaleValue(_Capital):
    def __init__(
        self,
        per: SizedDimension,
        product: _Product,
        gross_value: float | str | Decimal | None = None,
        net_value: float | str | Decimal | None = None,
        currency: Currency = Currency.BASE,
    ) -> None:
        super().__init__(
            gross_value=gross_value, net_value=net_value, currency=currency
        )

        self.product = product
        self.per = per


__all__ = [
    "Currency",
    "CurrencyRefresh",
    "LabourCost",
    "OrderlineValue",
    "ProductionCost",
    "PurchaseCost",
]

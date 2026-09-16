from decimal import Decimal
from enum import StrEnum

from .durations import Duration
from .measures import SizedDimension


class CurrencyRefresh(StrEnum):
    EVERY_RUN = "EVERY RUN"
    HOURLY = "HOURLY"
    DAILY = "DAILY"
    MONTHLY = "MONTHLY"
    ONCE = "ONCE"


class Currency(StrEnum):
    NON = "No set currency. All Conversions are 1:1"
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


class _Capital:
    def __init__(
        self,
        amount: float | str | Decimal,
        currency: Currency = Currency.NON,
    ) -> None:
        self.amount = amount
        self.currency = currency


class PurchaseCost(_Capital):
    def __init__(
        self,
        amount: float | str | Decimal,
        per_unit: SizedDimension,
        currency: Currency = Currency.NON,
    ) -> None:
        super().__init__(amount, currency)
        self.per_unit = per_unit


class ProductionCost(_Capital):
    def __init__(
        self,
        amount: float | str | Decimal,
        per_unit: SizedDimension | None,
        per_time: Duration | None,
        currency: Currency = Currency.NON,
    ) -> None:
        super().__init__(amount, currency)

        if per_time is None and per_unit is None:
            raise ValueError(
                "ProductionCost must specify one of materials units produced"
                " or a time duration"
            )
        elif per_time is not None and per_unit is not None:
            raise ValueError(
                "Cannot specify production costs in both time and per unit. An"
                " aggregate figure needs to be specified for one of them only."
            )


class OrderValue(_Capital):
    def __init__(
        self,
        amount: float | str | Decimal,
        currency: Currency = Currency.NON,
    ) -> None:
        super().__init__(amount, currency)


class SaleValue(_Capital):
    def __init__(
        self,
        amount: float | str | Decimal,
        per: SizedDimension,
        currency: Currency = Currency.NON,
    ) -> None:
        super().__init__(amount, currency)
        self.per = per


__all__ = ["Currency", "OrderValue", "ProductionCost", "PurchaseCost"]

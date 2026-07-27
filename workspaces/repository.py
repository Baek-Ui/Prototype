"""보이스피싱 사례 저장소.

Protocol 뒤에 인메모리 Mock 구현을 둔다. 추후 SupabasePhishingRepository를
동일 시그니처로 추가하면 호출부 수정 없이 교체된다.
"""

from typing import List, Protocol

from .domain import PhishingCase, PhishingCategory, SimilarCase
from .embedding import cosine_similarity, embed


class PhishingRepository(Protocol):
    async def search_similar(
        self, embedding: List[float], top_k: int = 3
    ) -> List[SimilarCase]: ...

    async def list_all_cases(self) -> List[PhishingCase]: ...


# (텍스트, 카테고리, 출처) — 공개 보도자료에 인용된 대표 수법을 참고해 재구성
_SEED: List[tuple] = [
    # 기관사칭
    ("서울중앙지검 수사관입니다. 귀하 명의 계좌가 범죄에 연루되어 안전계좌로 이체가 필요합니다.", PhishingCategory.IMPERSONATION, "금융감독원"),
    ("금융감독원입니다. 계좌 동결 방지를 위해 즉시 자산을 안전계좌로 옮기셔야 합니다.", PhishingCategory.IMPERSONATION, "금융감독원"),
    ("경찰청 사이버수사대입니다. 수사 협조를 위해 통화 내용은 절대 발설하지 마십시오.", PhishingCategory.IMPERSONATION, "경찰청"),
    ("검찰 조사 대상자입니다. 지금 앱을 설치하고 원격제어를 허용해 주세요.", PhishingCategory.IMPERSONATION, "경찰청"),
    ("국세청입니다. 세금 환급을 위해 계좌번호와 주민등록번호를 알려주세요.", PhishingCategory.IMPERSONATION, "금융감독원"),
    # 대출사기
    ("저금리 대환대출 승인되었습니다. 기존 대출 상환을 위해 지정 계좌로 입금하세요.", PhishingCategory.LOAN, "금융감독원"),
    ("신용등급 상향 작업비가 필요합니다. 선입금 후 대출이 실행됩니다.", PhishingCategory.LOAN, "금융감독원"),
    ("정부지원 서민대출 대상자로 선정되었습니다. 보증보험료를 먼저 납부해 주세요.", PhishingCategory.LOAN, "금융감독원"),
    ("무직자도 당일 대출 가능합니다. 신분증 사본과 통장 사본을 보내주세요.", PhishingCategory.LOAN, "금융감독원"),
    ("대출 한도 상향을 위해 기존 대출금을 먼저 상환해야 합니다. 계좌 안내드립니다.", PhishingCategory.LOAN, "금융감독원"),
    # 가족사칭
    ("엄마 나 폰 액정 깨져서 수리 맡겼어. 이 번호로 카톡 줘.", PhishingCategory.FAMILY, "경찰청"),
    ("아빠 급하게 돈이 필요한데 지금 통화가 안 돼. 계좌로 200만원만 보내줘.", PhishingCategory.FAMILY, "경찰청"),
    ("나 지금 친구 보증 때문에 급해. 신분증 사진이랑 계좌 비밀번호 좀 보내줘.", PhishingCategory.FAMILY, "경찰청"),
    ("엄마 나 사고 났어. 합의금이 필요한데 지금 바로 송금해줘.", PhishingCategory.FAMILY, "경찰청"),
    # 스미싱
    ("[Web발신] 택배 배송 주소 불일치. 아래 링크에서 정보를 수정해 주세요. http://bit.ly/ab12cd", PhishingCategory.SMISHING, "한국인터넷진흥원"),
    ("[국민지원금] 신청 대상자입니다. 링크 접속 후 본인인증을 완료해 주세요. http://gov-kr.co", PhishingCategory.SMISHING, "한국인터넷진흥원"),
    ("결제 완료 안내: 39,000원. 본인이 아닐 경우 아래 링크를 눌러 취소하세요. http://pay-cancel.net", PhishingCategory.SMISHING, "한국인터넷진흥원"),
    ("모바일 청첩장이 도착했습니다. 확인하기 http://invite-card.info", PhishingCategory.SMISHING, "한국인터넷진흥원"),
    ("건강보험공단 환급금 조회 안내입니다. 앱을 설치하고 본인인증하세요.", PhishingCategory.SMISHING, "한국인터넷진흥원"),
    # 정상 (대조군)
    ("안녕하세요, 내일 회의 시간 오후 3시로 변경 가능할까요?", PhishingCategory.NORMAL, "자체 구성"),
    ("주문하신 상품이 오늘 출고되었습니다. 배송 조회는 앱에서 확인하실 수 있습니다.", PhishingCategory.NORMAL, "자체 구성"),
    ("이번 주말에 같이 저녁 먹을래? 시간 되면 알려줘.", PhishingCategory.NORMAL, "자체 구성"),
    ("[신한은행] 03/15 10:23 입금 500,000원 잔액 1,234,567원", PhishingCategory.NORMAL, "자체 구성"),
    ("관리비 고지서가 발행되었습니다. 납부 기한은 이달 25일입니다.", PhishingCategory.NORMAL, "자체 구성"),
    ("건강검진 예약이 확정되었습니다. 방문 시 신분증을 지참해 주세요.", PhishingCategory.NORMAL, "자체 구성"),
]


class MockPhishingRepository:
    """실제 DB 연동 전까지 사용하는 인메모리 저장소."""

    def __init__(self) -> None:
        self._cases = [
            PhishingCase(
                id=f"case-{index:03d}",
                text=text,
                category=category,
                is_phishing=category is not PhishingCategory.NORMAL,
                source=source,
                embedding=embed(text),
            )
            for index, (text, category, source) in enumerate(_SEED)
        ]

    async def list_all_cases(self) -> List[PhishingCase]:
        return list(self._cases)

    async def search_similar(
        self, embedding: List[float], top_k: int = 3
    ) -> List[SimilarCase]:
        scored = [
            SimilarCase(case=case, similarity=cosine_similarity(embedding, case.embedding))
            for case in self._cases
        ]
        scored.sort(key=lambda item: item.similarity, reverse=True)
        return scored[:top_k]

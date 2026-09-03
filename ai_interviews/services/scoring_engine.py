class ScoringEngine:

    RELEVANCE_WEIGHT = 0.4
    COMPLETENESS_WEIGHT = 0.3
    KEYWORD_WEIGHT = 0.3

    def calculate_final_score(
        self,
        relevance_score,
        completeness_score,
        keyword_score
    ):
        final_score = (
            relevance_score * self.RELEVANCE_WEIGHT
            + completeness_score * self.COMPLETENESS_WEIGHT
            + keyword_score * self.KEYWORD_WEIGHT
        )

        return round(final_score, 2)

    def calculate_keyword_score(self, answer, keywords):
        if not keywords:
            return 0

        answer = answer.lower()

        matched_keywords = sum(
            1
            for keyword in keywords
            if keyword.lower() in answer
        )

        score = (matched_keywords / len(keywords)) * 100

        return round(score, 2)

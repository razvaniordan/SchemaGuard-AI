"""Priority-based rule catalogue for interchange classification."""

from __future__ import annotations

from collections.abc import Iterable, Iterator

from models import CategoryDefinition, EU_PHASE_1_CATEGORY_DEFINITIONS


EXPECTED_RULE_PRIORITIES: tuple[int, ...] = tuple(range(1, 15))
DEFAULT_RULE_PRIORITY = 14


class PriorityRuleCatalogue:
    """Validated catalogue of interchange category rules.

    Rules are always exposed in ascending priority order:
    priority 1 is evaluated first, priority 14 is the default fallback.
    """

    def __init__(
        self,
        rules: Iterable[CategoryDefinition],
        *,
        expected_priorities: tuple[int, ...] = EXPECTED_RULE_PRIORITIES,
        default_priority: int = DEFAULT_RULE_PRIORITY,
    ) -> None:
        self._expected_priorities = expected_priorities
        self._default_priority = default_priority
        self._rules = tuple(sorted(rules, key=lambda rule: rule.priority))
        self._rules_by_priority = {rule.priority: rule for rule in self._rules}

        self._validate()

    def _validate(self) -> None:
        priorities = [rule.priority for rule in self._rules]
        unique_priorities = set(priorities)
        expected_priorities = set(self._expected_priorities)

        if len(priorities) != len(unique_priorities):
            duplicates = sorted(
                priority for priority in unique_priorities if priorities.count(priority) > 1
            )
            raise ValueError(f"Rule catalogue contains duplicate priorities: {duplicates}")

        if unique_priorities != expected_priorities:
            missing = sorted(expected_priorities - unique_priorities)
            unexpected = sorted(unique_priorities - expected_priorities)

            raise ValueError(
                "Rule catalogue must contain priorities "
                f"{list(self._expected_priorities)}. "
                f"Missing={missing}, unexpected={unexpected}"
            )

        if self._default_priority not in self._rules_by_priority:
            raise ValueError(
                f"Rule catalogue must contain default priority {self._default_priority}"
            )

    def __len__(self) -> int:
        return len(self._rules)

    def __iter__(self) -> Iterator[CategoryDefinition]:
        return self.iter_by_priority()

    @property
    def min_priority(self) -> int:
        return min(self._expected_priorities)

    @property
    def max_priority(self) -> int:
        return max(self._expected_priorities)

    @property
    def default_priority(self) -> int:
        return self._default_priority

    def iter_by_priority(self) -> Iterator[CategoryDefinition]:
        """Return rules in evaluation order."""

        return iter(self._rules)

    def get_all(self) -> tuple[CategoryDefinition, ...]:
        """Return all rules in priority order."""

        return self._rules

    def get_by_priority(self, priority: int) -> CategoryDefinition | None:
        """Return a rule by priority, or None when it does not exist."""

        return self._rules_by_priority.get(priority)

    def get_required_by_priority(self, priority: int) -> CategoryDefinition:
        """Return a rule by priority, raising an error when missing."""

        rule = self.get_by_priority(priority)

        if rule is None:
            raise KeyError(f"No rule configured for priority {priority}")

        return rule

    def get_default_rule(self) -> CategoryDefinition:
        """Return the default fallback rule."""

        return self.get_required_by_priority(self._default_priority)

    def as_api_response(self) -> list[dict[str, object]]:
        """Serialize catalogue for REST responses."""

        return [
            rule.model_dump(by_alias=True, mode="json")
            for rule in self._rules
        ]


EU_PHASE_1_RULE_CATALOGUE = PriorityRuleCatalogue(
    EU_PHASE_1_CATEGORY_DEFINITIONS,
)
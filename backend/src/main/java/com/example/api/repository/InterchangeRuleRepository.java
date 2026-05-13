package com.example.api.repository;

import com.example.api.entity.InterchangeRule;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.Optional;

public interface InterchangeRuleRepository extends JpaRepository<InterchangeRule, Long> {

    @Query(value = """
            SELECT r.*
            FROM interchange_rules r
            WHERE (:cardNetworkId IS NULL OR r.card_network_id IS NULL OR r.card_network_id = :cardNetworkId)
              AND (:mccCode IS NULL OR r.mcc_code IS NULL OR r.mcc_code = :mccCode)
              AND (:cardTypeId IS NULL OR r.card_type_id IS NULL OR r.card_type_id = :cardTypeId)
              AND (:transactionChannel IS NULL OR r.transaction_channel IS NULL OR r.transaction_channel = :transactionChannel)
              AND (:regionCode IS NULL OR r.region_code IS NULL OR r.region_code = :regionCode)
              AND (:is3dsAuthenticated IS NULL OR r.is_3ds_required IS NULL OR r.is_3ds_required = :is3dsAuthenticated)
              AND (:clearingTimeCondition IS NULL OR r.clearing_time_condition IS NULL OR r.clearing_time_condition = :clearingTimeCondition)
            ORDER BY r.rule_priority ASC
            LIMIT 1
            """, nativeQuery = true)
    Optional<InterchangeRule> findBestMatchingRule(
            @Param("cardNetworkId") Long cardNetworkId,
            @Param("mccCode") String mccCode,
            @Param("cardTypeId") Long cardTypeId,
            @Param("transactionChannel") String transactionChannel,
            @Param("regionCode") String regionCode,
            @Param("is3dsAuthenticated") String is3dsAuthenticated,
            @Param("clearingTimeCondition") String clearingTimeCondition
    );
}
package com.example.api.repository;

import com.example.api.entity.Transaction;
import com.example.api.entity.Transaction.TransactionChannel;
import com.example.api.entity.Transaction.TransactionStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface TransactionRepository extends JpaRepository<Transaction, Long> {

	@Override
    @EntityGraph(attributePaths = {
            "merchant",
            "merchant.country",
            "card",
            "card.cardType",
            "issuerBank",
            "issuerBank.country",
            "cardNetwork",
            "mccCode",
            "region"
    })
    List<Transaction> findAll();

	@EntityGraph(attributePaths = {
			"client",
			"merchant",
			"card",
			"acquiringPartner",
			"issuerBank",
			"cardNetwork",
			"mccCode",
			"region"
	})
	@Query(
			value = """
					select t
					from Transaction t
				where (
					:searchTerm is null or :searchTerm = '' or
				(:numericSearch = true and t.transactionId = :transactionId) or
				lower(coalesce(t.client.clientName, '')) like lower(concat('%', :searchTerm, '%')) or
				lower(coalesce(t.merchant.merchantName, '')) like lower(concat('%', :searchTerm, '%'))
				)
				and (:channel is null or t.transactionChannel = :channel)
				and (:is3ds is null or t.is3dsAuthenticated = :is3ds)
				and (:status is null or t.transactionStatus = :status)
					""",
			countQuery = """
					select count(t)
					from Transaction t
				where (
					:searchTerm is null or :searchTerm = '' or
				(:numericSearch = true and t.transactionId = :transactionId) or
				lower(coalesce(t.client.clientName, '')) like lower(concat('%', :searchTerm, '%')) or
				lower(coalesce(t.merchant.merchantName, '')) like lower(concat('%', :searchTerm, '%'))
				)
				and (:channel is null or t.transactionChannel = :channel)
				and (:is3ds is null or t.is3dsAuthenticated = :is3ds)
				and (:status is null or t.transactionStatus = :status)
					"""
	)
    Page<Transaction> findPageBySearchTerm(
    	@Param("searchTerm") String searchTerm,
    	@Param("numericSearch") boolean numericSearch,
    	@Param("transactionId") Long transactionId,
        @Param("channel") TransactionChannel channel,
        @Param("is3ds") String is3ds,
        @Param("status") TransactionStatus status,
    	Pageable pageable
    	);
}

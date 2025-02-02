#pragma once
#include <hive/chain/account_object.hpp>
#include <hive/chain/block_summary_object.hpp>
#include <hive/chain/comment_object.hpp>
#include <hive/chain/global_property_object.hpp>
#include <hive/chain/hive_objects.hpp>
#include <hive/chain/transaction_object.hpp>
#include <hive/chain/witness_objects.hpp>
#include <hive/chain/database.hpp>

namespace hive { namespace plugins { namespace block_api {

using namespace hive::chain;

struct api_signed_block : public signed_block_header
{
  api_signed_block( const signed_block& block ) : signed_block_header( block )
  {
    for( const auto& trx : block.transactions )
      transactions.push_back( trx.trx );
  }
  api_signed_block() {}

  vector<signed_transaction> transactions;
};

struct api_signed_block_object : public api_signed_block
{
  api_signed_block_object( const signed_block& block ) : api_signed_block( block )
  {
    block_id = id();
    signing_key = signee();
    transaction_ids.reserve( transactions.size() );
    for( const auto& tx : transactions )
      transaction_ids.push_back( tx.id() );
  }
  api_signed_block_object() {}

  block_id_type                 block_id;
  public_key_type               signing_key;
  vector< transaction_id_type > transaction_ids;
};

} } } // hive::plugins::database_api

FC_REFLECT_DERIVED( hive::plugins::block_api::api_signed_block, (hive::protocol::signed_block_header),
              (transactions)
            )

FC_REFLECT_DERIVED( hive::plugins::block_api::api_signed_block_object, (hive::plugins::block_api::api_signed_block),
              (block_id)
              (signing_key)
              (transaction_ids)
            )

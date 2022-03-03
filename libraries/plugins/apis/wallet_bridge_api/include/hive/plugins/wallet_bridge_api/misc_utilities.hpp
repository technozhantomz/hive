#pragma once

#include <fc/variant.hpp>

#include <hive/protocol/asset.hpp>
#include <hive/plugins/wallet_bridge_api/wallet_bridge_api_args.hpp>

#include<vector>
#include<string>
#include<functional>
#include <iomanip>

namespace hive { namespace plugins { namespace wallet_bridge_api {

using std::function;
using fc::variant;
using std::string;
using hive::protocol::asset;
using std::setiosflags;
using std::ios;
using std::setw;
using std::endl;

struct wallet_formatter
{
  template<typename T>
  static variant get_result( const std::stringstream& out_text, const T& out_json, format_type format )
  {
    if( format == format_type::text )
    {
      return variant( out_text.str() );
    }
    else//format_type::json
    {
      variant _result;
      to_variant( out_json, _result );
      return _result;
    }
  }

  static string help( variant result )
  {
    return result.get_string();
  }

  static string get_help( variant result )
  {
    return result.get_string();
  }

  static variant list_my_accounts( const serializer_wrapper<vector<database_api::api_account_object>>& accounts, format_type format )
  {
    std::stringstream             out_text;
    list_my_accounts_json_return  out_json;

    asset total_hive;
    asset total_vest(0, VESTS_SYMBOL );
    asset total_hbd(0, HBD_SYMBOL );
    for( const auto& account_in_wrapper : accounts.value ) {
      auto a = account_in_wrapper;
      total_hive += a.balance;
      total_vest += a.vesting_shares;
      total_hbd  += a.hbd_balance;

      if( format == format_type::text )
      {
        out_text << std::left << setw(17) << string(a.name)
            << std::right << setw(18) << hive::protocol::legacy_asset::from_asset(a.balance).to_string() <<" "
            << std::right << setw(26) << hive::protocol::legacy_asset::from_asset(a.vesting_shares).to_string() <<" "
            << std::right << setw(16) << hive::protocol::legacy_asset::from_asset(a.hbd_balance).to_string() <<"\n";
      }
      else//format_type::json
      {
        out_json.accounts.emplace_back( list_my_accounts_json_account{ a.name, a.balance, a.vesting_shares, a.hbd_balance } );
      }
    }

    if( format == format_type::text )
    {
      out_text << "-------------------------------------------------------------------------------\n";
      out_text << std::left << setw(17) << "TOTAL"
          << std::right << setw(18) << hive::protocol::legacy_asset::from_asset(total_hive).to_string() <<" "
          << std::right << setw(26) << hive::protocol::legacy_asset::from_asset(total_vest).to_string() <<" "
          << std::right << setw(16) << hive::protocol::legacy_asset::from_asset(total_hbd).to_string() <<"\n";
    }
    else//format_type::json
    {
      out_json.total_hive = total_hive;
      out_json.total_vest = total_vest;
      out_json.total_hbd  = total_hbd;
    }

    return get_result( out_text, out_json, format );
  }

  static string get_account_history( variant result )
  {
    std::stringstream ss;
    ss << std::left << setw( 8 )  << "#" << " ";
    ss << std::left << setw( 10 ) << "BLOCK #" << " ";
    ss << std::left << setw( 50 ) << "TRX ID" << " ";
    ss << std::left << setw( 20 ) << "OPERATION" << " ";
    ss << std::left << setw( 50 ) << "DETAILS" << "\n";
    ss << "---------------------------------------------------------------------------------------------------\n";
    const auto& results = result.get_array();

    auto _get_op_content = []( bool legacy_style_exists, const variant& op )
    {
      if( legacy_style_exists )
      {
        const auto& opop = op["op"].get_array();
        return std::make_pair( opop[0].as_string(), fc::json::to_string(opop[1]) );
      }
      else
      {
        const auto& opop = op["op"].get_object();
        return std::make_pair( opop["type"].as_string(), fc::json::to_string(opop["value"]) );
      }
    };

    for( const auto& item : results )
    {
      ss << std::left << setw(8) << item.get_array()[0].as_string() << " ";
      const auto& op = item.get_array()[1].get_object();
      ss << std::left << setw(10) << op["block"].as_string() << " ";
      ss << std::left << setw(50) << op["trx_id"].as_string() << " ";

      auto _op_content = _get_op_content( true/*legacy_style_exists*/, op );
      ss << std::left << setw(20) << _op_content.first << " ";
      ss << std::left << setw(50) << _op_content.second << "\n";
    }
    return ss.str();
  }

  static string get_open_orders( variant result )
  {
    auto orders = result.as< vector< serializer_wrapper<database_api::api_limit_order_object> > >();
    std::stringstream ss;

    ss << setiosflags( ios::fixed ) << setiosflags( ios::left ) ;
    ss << ' ' << setw( 10 ) << "Order #";
    ss << ' ' << setw( 12 ) << "Price";
    ss << ' ' << setw( 14 ) << "Quantity";
    ss << ' ' << setw( 10 ) << "Type";
    ss << "\n===============================================================================\n";
    for( const auto& order_in_wrapper : orders )
    {
      auto o = order_in_wrapper.value;
      ss << ' ' << setw( 10 ) << o.orderid;
      ss << ' ' << setw( 14 ) << hive::protocol::legacy_asset::from_asset( asset( o.for_sale, o.sell_price.base.symbol ) ).to_string();
      ss << ' ' << setw( 10 ) << (o.sell_price.base.symbol == HIVE_SYMBOL ? "SELL" : "BUY");
      ss << "\n";
    }
    return ss.str();
  }

  static string get_order_book( variant result )
  {
    auto orders_in_wrapper = result.as< serializer_wrapper<get_order_book_return> >();
    auto orders = orders_in_wrapper.value;
    std::stringstream ss;
    asset bid_sum = asset( 0, HBD_SYMBOL );
    asset ask_sum = asset( 0, HBD_SYMBOL );
    int spacing = 16;

    ss << setiosflags( ios::fixed ) << setiosflags( ios::left ) ;

    ss << ' ' << setw( ( spacing * 4 ) + 6 ) << "Bids" << "Asks\n"
      << ' '
      << setw( spacing + 3 ) << "Sum(HBD)"
      << setw( spacing + 1 ) << "HBD"
      << setw( spacing + 1 ) << "HIVE"
      << setw( spacing + 1 ) << "Price"
      << setw( spacing + 1 ) << "Price"
      << setw( spacing + 1 ) << "HIVE "
      << setw( spacing + 1 ) << "HBD " << "Sum(HBD)"
      << "\n====================================================================="
      << "|=====================================================================\n";

    for( size_t i = 0; i < orders.bids.size() || i < orders.asks.size(); i++ )
    {
      if( i < orders.bids.size() )
      {
        bid_sum += asset( orders.bids[i].hbd, HBD_SYMBOL );
        ss
          << ' ' << setw( spacing ) << hive::protocol::legacy_asset::from_asset(bid_sum).to_string()
          << ' ' << setw( spacing ) << hive::protocol::legacy_asset::from_asset(asset( orders.bids[i].hbd, HBD_SYMBOL)).to_string()
          << ' ' << setw( spacing ) << hive::protocol::legacy_asset::from_asset(asset( orders.bids[i].hive, HIVE_SYMBOL)).to_string();
      }
      else
      {
        ss << setw( (spacing * 4 ) + 5 ) << ' ';
      }

      ss << " |";

      if( i < orders.asks.size() )
      {
        ask_sum += asset(orders.asks[i].hbd, HBD_SYMBOL);
        ss
          << ' ' << setw( spacing ) << hive::protocol::legacy_asset::from_asset(asset( orders.asks[i].hive, HIVE_SYMBOL )).to_string()
          << ' ' << setw( spacing ) << hive::protocol::legacy_asset::from_asset(asset( orders.asks[i].hbd, HBD_SYMBOL )).to_string()
          << ' ' << setw( spacing ) << hive::protocol::legacy_asset::from_asset(ask_sum).to_string();
      }

      ss << endl;
    }

    ss << endl
      << "Bid Total: " << hive::protocol::legacy_asset::from_asset(bid_sum).to_string() << endl
      << "Ask Total: " << hive::protocol::legacy_asset::from_asset(ask_sum).to_string() << endl;

    return ss.str();
  }

  static string get_withdraw_routes( variant result )
  {
    auto routes = result.as< vector< database_api::api_withdraw_vesting_route_object > >();
    std::stringstream ss;

    ss << ' ' << std::left << setw( 18 ) << "From";
    ss << ' ' << std::left << setw( 18 ) << "To";
    ss << ' ' << std::right << setw( 8 ) << "Percent";
    ss << ' ' << std::right << setw( 9 ) << "Auto-Vest";
    ss << "\n=========================================================\n";

    for( auto& r : routes )
    {
      ss << ' ' << std::left << setw( 18 ) << string( r.from_account );
      ss << ' ' << std::left << setw( 18 ) << string( r.to_account );
      ss << ' ' << std::right << setw( 8 ) << std::setprecision( 2 ) << std::fixed << double( r.percent ) / 100;
      ss << ' ' << std::right << setw( 9 ) << ( r.auto_vest ? "true" : "false" ) << std::endl;
    }

    return ss.str();
  }

};

} } } //hive::plugins::wallet_bridge_api

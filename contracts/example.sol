pragma solidity ^0.8.12;

contract example {


    string private a;

    function storeMessage(string memory b) public {
        a=b;
    }

    function printMessage() public view returns(string memory) {
        return(a);
    }

}